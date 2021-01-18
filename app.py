#!/usr/bin/env python3
# thoth-build-watcher
# Copyright(C) 2019, 2020 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A build watch - watch for builds and submit images to Thoth for analysis."""

import os
import sys
import logging
import time
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Manager
from requests.exceptions import HTTPError

import click

from thamos.lib import build_analysis
from thamos.config import config as configuration
from thamos import __version__ as __thamos_version__
from thoth.common import init_logging
from thoth.common import OpenShift
from thoth.common import __version__ as __common_version__
from thoth.analyzer import __version__ as __analyzer_version__
from thoth.analyzer import run_command
from thoth.analyzer import CommandError
from prometheus_client import CollectorRegistry, Counter, push_to_gateway

init_logging()
prometheus_registry = CollectorRegistry()

__version__ = "0.7.0"
__component_version__ = (
    f"{__version__}+" f"common.{__common_version__}." f"analyzer.{__analyzer_version__}." f"thamos.{__thamos_version__}"
)

_LOGGER = logging.getLogger("thoth.build_watcher")

_HERE_DIR = os.path.dirname(os.path.abspath(__file__))
_SKOPEO_EXEC_PATH = os.getenv("SKOPEO_EXEC_PATH", os.path.join(_HERE_DIR, "bin", "skopeo"))
_THOTH_METRICS_PUSHGATEWAY_URL = os.getenv("PROMETHEUS_PUSHGATEWAY_HOST")

_METRIC_IMAGES_SUBMITTED = Counter(
    "build_watcher_image_submission_total", "Number of images submitted for analysis.", [], registry=prometheus_registry
)
_METRIC_IMAGES_PUSHED_REGISTRY = Counter(
    "build_watcher_image_pushed_registry_total",
    "Number of images push to external registry.",
    [],
    registry=prometheus_registry,
)
_METRIC_BUILD_LOGS_SUBMITTED = Counter(
    "build_watcher_build_log_submission_total",
    "Number of build logs submitted for analysis.",
    [],
    registry=prometheus_registry,
)
_METRIC_BUILDS_FAILED = Counter(
    "build_watcher_builds_failed_total", "Number of builds failed.", [], registry=prometheus_registry
)


def _buildlog_metadata(api_endpoint: str = None, build_log: str = None) -> dict:
    """Gather metadata for the build log."""
    # Update the metadata with more details
    if not build_log:
        return {}
    return {"apiversion": api_endpoint, "kind": "BuildLog", "log": build_log, "metadata": "string"}


def _existing_producer(queue: Queue, build_watcher_namespace: str) -> None:
    """Query for existing images in image streams and queue them for analysis."""
    openshift = OpenShift()
    v1_imagestreams = openshift.ocp_client.resources.get(api_version="image.openshift.io/v1", kind="ImageStream")
    for item in v1_imagestreams.get(namespace=build_watcher_namespace).items:
        _LOGGER.debug("Found imagestream item: %s", str(item))
        _LOGGER.debug("Listing tags available for %r", item["metadata"]["name"])
        for tag_info in item.status.tags or []:
            output_reference = f"{item.status.dockerImageRepository}:{tag_info.tag}"
            _LOGGER.info("Queueing already existing image %r for analysis", output_reference)
            queue.put(output_reference)

    _LOGGER.info("Queuing existing images for analyses has finished, all of them were scheduled for analysis")


def _get_build(openshift, strategy: dict, build_reference: dict, event_metadata: dict) -> dict:
    """Gather Build log and Base Image based upon the strategy of the build."""
    if strategy.get("sourceStrategy"):
        build_reference["base_input_reference"] = strategy.get("sourceStrategy", {}).get("from", {}).get("name", None)
    elif strategy.get("dockerStrategy") and strategy.get("dockerStrategy", {}).get("from", {}):
        build_reference["base_input_reference"] = strategy.get("dockerStrategy", {}).get("from", {}).get("name", None)
    else:
        build_reference["base_input_reference"] = None
    try:
        build_log = openshift.get_build_log(
            build_id=event_metadata.get("name"), namespace=event_metadata.get("namespace")
        )
    except HTTPError as exc:
        _LOGGER.warning("Failed to get the log for build %s: %s", event_metadata.get("name"), str(exc))
        build_log = None
    except Exception as exc:
        _LOGGER.exception("Failed to get the log for build %s: %s", event_metadata.get("name"), str(exc))
        build_log = None
    build_reference["build_log_reference"] = _buildlog_metadata(event_metadata.get("selfLink"), build_log)

    return build_reference


def _event_producer(queue: Queue, build_watcher_namespace: str) -> None:
    """Accept events from the cluster and queue them into work queue processed by the main process."""
    _LOGGER.info("Starting event producer")
    openshift = OpenShift()
    v1_build = openshift.ocp_client.resources.get(api_version="build.openshift.io/v1", kind="Build")
    for event in v1_build.watch(namespace=build_watcher_namespace):
        event_name = event["object"].metadata.name
        build_reference = {
            "build_log_reference": _buildlog_metadata(),
            "base_input_reference": None,
            "output_reference": None,
        }
        if event["object"].status.phase != "Complete":
            _LOGGER.debug(
                "Ignoring build event for %r - not completed phase %r", event_name, event["object"].status.phase
            )
            continue
        elif event["object"].status.phase == "Failed":
            _LOGGER.debug(
                "Submitting base_image and build_log as build event for %r - the phase is %r",
                event_name,
                event["object"].status.phase,
            )
            strategy = event["object"].spec.strategy
            build_reference = _get_build(openshift, strategy, build_reference, event["object"].metadata)
            _LOGGER.info("Queueing build log based on build event %r for further processing", event_name)
            _METRIC_BUILDS_FAILED.inc()
            try:
                _LOGGER.info("Submitting metrics to Prometheus pushgateway %r", _THOTH_METRICS_PUSHGATEWAY_URL)
                push_to_gateway(_THOTH_METRICS_PUSHGATEWAY_URL, job="build-watcher", registry=prometheus_registry)
            except Exception as e:
                _LOGGER.exception(f"An error occurred pushing the metrics: {str(e)}")
            queue.put(build_reference)
            continue

        _LOGGER.debug("New build event: %s", str(event))
        build_reference["output_reference"] = event["object"].status.outputDockerImageReference
        strategy = event["object"].spec.strategy
        build_reference = _get_build(openshift, strategy, build_reference, event["object"].metadata)
        _LOGGER.info("Queueing build log based on build event %r for further processing", event_name)
        queue.put(build_reference)


def _do_analyze_build(
    output_reference: str,
    build_log_reference: str,
    base_input_reference: str,
    push_registry: str = None,
    *,
    environment_type: str = None,
    src_registry_user: str = None,
    src_registry_password: str = None,
    dst_registry_user: str = None,
    dst_registry_password: str = None,
    src_verify_tls: bool = True,
    dst_verify_tls: bool = True,
    debug: bool = False,
    force: bool = False,
) -> None:
    if push_registry:
        _LOGGER.info("Pushing output image %r to an external push registry %r", output_reference, push_registry)
        output_reference = _push_image(
            output_reference,
            push_registry,
            src_registry_user,
            src_registry_password,
            dst_registry_user,
            dst_registry_password,
            src_verify_tls=src_verify_tls,
            dst_verify_tls=dst_verify_tls,
        )
        if output_reference:
            _METRIC_IMAGES_PUSHED_REGISTRY.inc()
            _LOGGER.info("Successfully pushed output image to %r", output_reference)

        if base_input_reference:
            _LOGGER.info("Pushing base image %r to an external push registry %r", base_input_reference, push_registry)
            base_input_reference = _push_image(
                base_input_reference,
                push_registry,
                src_registry_user,
                src_registry_password,
                dst_registry_user,
                dst_registry_password,
                src_verify_tls=src_verify_tls,
                dst_verify_tls=dst_verify_tls,
            )
            if base_input_reference:
                _METRIC_IMAGES_PUSHED_REGISTRY.inc()
                _LOGGER.info("Successfully pushed base image to %r", base_input_reference)

    analysis_response = build_analysis(
        build_log=build_log_reference,
        base_image=base_input_reference,
        base_registry_password=src_registry_password,
        base_registry_user=src_registry_user,
        base_registry_verify_tls=src_verify_tls,
        environment_type=environment_type,
        nowait=True,
        output_image=output_reference,
        output_registry_password=dst_registry_password,
        output_registry_user=dst_registry_user,
        output_registry_verify_tls=dst_verify_tls,
        force=force,
        debug=debug,
    )

    if analysis_response.base_image_analysis.analysis_id:
        _METRIC_IMAGES_SUBMITTED.inc()
    if analysis_response.build_log_analysis.analysis_id:
        _METRIC_BUILD_LOGS_SUBMITTED.inc()
    if analysis_response.output_image_analysis.analysis_id:
        _METRIC_IMAGES_SUBMITTED.inc()

    if _THOTH_METRICS_PUSHGATEWAY_URL:
        try:
            _LOGGER.info("Submitting metrics to Prometheus pushgateway %r", _THOTH_METRICS_PUSHGATEWAY_URL)
            push_to_gateway(_THOTH_METRICS_PUSHGATEWAY_URL, job="build-watcher", registry=prometheus_registry)
        except Exception as e:
            _LOGGER.exception(f"An error occurred pushing the metrics: {str(e)}")
    else:
        _LOGGER.info("Not pushing metrics as Prometheus pushgateway was not provided")

    _LOGGER.info(
        "Successfully submitted %r, %r, build_log, to Thoth for analysis; analysis ids respectively: %r, %r, %r",
        output_reference,
        base_input_reference,
        analysis_response.output_image_analysis.analysis_id,
        analysis_response.base_image_analysis.analysis_id,
        analysis_response.buildlog_analysis.analysis_id,
        analysis_response.buildlog_document_id,
    )


def _push_image(
    image: str,
    push_registry: str,
    src_registry_user: str = None,
    src_registry_password: str = None,
    dst_registry_user: str = None,
    dst_registry_password: str = None,
    src_verify_tls: bool = True,
    dst_verify_tls: bool = True,
) -> str:
    """Push the given image (fully specified with registry info) into another registry."""
    cmd = f"{_SKOPEO_EXEC_PATH} --insecure-policy copy "

    if not src_verify_tls:
        cmd += "--src-tls-verify=false "

    if not dst_verify_tls:
        cmd += "--dest-tls-verify=false "

    if dst_registry_user or dst_registry_password:
        dst_registry_user = dst_registry_user or "build-watcher"
        cmd += f"--dest-creds={dst_registry_user}"

        if dst_registry_password:
            cmd += f":{dst_registry_password}"

        cmd += " "

    if src_registry_user or src_registry_password:
        src_registry_user = src_registry_user or "build-watcher"
        cmd += f"--src-creds={src_registry_user}"

        if dst_registry_password:
            cmd += f":{src_registry_password}"

        cmd += " "

    image_name = image.rsplit("/", maxsplit=1)[1]
    if "quay.io" in push_registry:
        image_name = image_name.replace("@sha256", "")
        output = f"{push_registry}:{image_name.replace(':','-')}"
    else:
        output = f"{push_registry}/{image_name}"
    _LOGGER.debug("Pushing image %r from %r to registry %r, output is %r", image_name, image, push_registry, output)
    cmd += f"docker://{image} docker://{output}"

    _LOGGER.debug("Running: %s", cmd)
    try:
        command = run_command(cmd)
        _LOGGER.debug("%s stdout:\n%s\n%s", _SKOPEO_EXEC_PATH, command.stdout, command.stderr)
    except CommandError as exc:
        if "Error determining manifest MIME type" in exc.stderr:
            # Manifest MIME type error is caused by the way image is build. we have no control over it.
            _LOGGER.warning("Ignoring error caused by invalid manifest MIME type during push: %s", str(exc))
            return
        else:
            _LOGGER.exception("Failed to push image %r to external registry: %s", image_name, str(exc))
    return output


def _submitter(
    queue: Queue,
    push_registry: str,
    environment_type: str,
    src_registry_user: str = None,
    src_registry_password: str = None,
    dst_registry_user: str = None,
    dst_registry_password: str = None,
    no_src_registry_tls_verify: bool = False,
    no_dst_registry_tls_verify: bool = False,
    debug: bool = False,
    force: bool = False,
) -> None:
    """Read messages from queue and submit each message with image to Thoth for analysis."""
    while True:
        reference = queue.get()
        if isinstance(reference, dict):
            build_log_reference = reference.get("build_log_reference", _buildlog_metadata())
            base_input_reference = reference.get("base_input_reference", None)
            output_reference = reference.get("output_reference", None)
        else:
            output_reference = reference
            build_log_reference = _buildlog_metadata()
            base_input_reference = None
            _LOGGER.info("Handling analysis of image %r", reference)

        try:
            _do_analyze_build(
                output_reference,
                build_log_reference,
                base_input_reference,
                push_registry,
                environment_type=environment_type,
                src_registry_user=src_registry_user,
                src_registry_password=src_registry_password,
                dst_registry_user=dst_registry_user,
                dst_registry_password=dst_registry_password,
                src_verify_tls=not no_src_registry_tls_verify,
                dst_verify_tls=not no_dst_registry_tls_verify,
                debug=debug,
                force=force,
            )
        except Exception as exc:
            _LOGGER.exception("Failed to submit image %r for analysis to Thoth: %s", output_reference, str(exc))


@click.command()
@click.option(
    "--verbose", "-v", is_flag=True, envvar="THOTH_VERBOSE_BUILD_WATCHER", help="Be verbose about what is going on."
)
@click.option(
    "--build-watcher-namespace",
    "-n",
    type=str,
    required=True,
    envvar="THOTH_WATCHED_NAMESPACE",
    help="Namespace to connect to to wait for events.",
)
@click.option(
    "--thoth-api-host",
    "-a",
    type=str,
    required=True,
    envvar="THOTH_USER_API_HOST",
    help="Host to Thoth's User API - API endpoint discovery will be transparently done.",
)
@click.option(
    "--no-tls-verify",
    "-T",
    is_flag=True,
    envvar="THOTH_NO_TLS_VERIFY",
    help="Do not check for TLS certificates when communicating with Thoth.",
)
@click.option(
    "--no-src-registry-tls-verify",
    "-S",
    is_flag=True,
    envvar="THOTH_NO_SOURCE_REGISTRY_TLS_VERIFY",
    help="Do not check for TLS certificates of registry when pulling images on Thoth side.",
)
@click.option(
    "--no-dst-registry-tls-verify",
    "-D",
    is_flag=True,
    envvar="THOTH_NO_DESTINATION_REGISTRY_TLS_VERIFY",
    help="Do not check for TLS certificates of registry when pushing to a remote push registry.",
)
@click.option(
    "--pass-token",
    "-p",
    is_flag=True,
    envvar="THOTH_PASS_TOKEN",
    help="Pass OpenShift token to User API to enable image pulling "
    "(disjoint with --registry-user and --registry-password).",
)
@click.option(
    "--src-registry-user",
    "-u",
    type=str,
    envvar="THOTH_SRC_REGISTRY_USER",
    help="Registry user used to pull images from defaults to destination registry user if push registry is not used.",
)
@click.option(
    "--src-registry-password",
    "-u",
    type=str,
    envvar="THOTH_SRC_REGISTRY_PASSWORD",
    help="Registry password used to pull images from, defaults to destination registry password if "
    "push registry is not used.",
)
@click.option(
    "--dst-registry-user",
    "-u",
    type=str,
    envvar="THOTH_DST_REGISTRY_USER",
    help="Registry user used to pull images on Thoht side.",
)
@click.option(
    "--dst-registry-password",
    "-u",
    type=str,
    envvar="THOTH_DST_REGISTRY_PASSWORD",
    help="Registry password used to pull images on Thoth side, it defaults to token in case of --pass-token is set.",
)
@click.option(
    "--push-registry",
    "-r",
    type=str,
    envvar="THOTH_PUSH_REGISTRY",
    help="Push images from the original registry into another registry and use this registry as a source for Thoth. "
    "This option is suitable if you want to analyze images from different cluster in which an internal registry "
    "is used without route being exposed. This way you can copy images from internal registry to a remote one "
    "where Thoth has access to. Thoth will use the push registry specified instead of the original one where "
    "images were pushed to. If credentials are required to push into push registry, "
    "see --registry-{user,password} configuration options.",
)
@click.option(
    "--analyze-existing",
    is_flag=True,
    envvar="THOTH_ANALYZE_EXISTING",
    help="List images which were already built in the cluster and submit them to Thoth for analysis. "
    "This is applicable for OpenShift's image streams only.",
)
@click.option(
    "--workers-count",
    type=int,
    default=1,
    envvar="THOTH_BUILD_WATCHER_WORKERS",
    help="Number of worker processes to submit image analysis in parallel.",
)
@click.option(
    "--environment-type",
    required=False,
    type=click.Choice(["runtime", "buildtime"]),
    default="runtime",
    show_default=True,
    envvar="THOTH_ENVIRONMENT_TYPE",
    help="Type of environment - type of images - runtime or buildtime analyzed in the namespace.",
)
@click.option(
    "--debug",
    is_flag=True,
    show_default=True,
    envvar="THOTH_BUILD_ANALYSIS_DEBUG",
    help="Run build analysis in debug mode.",
)
@click.option(
    "--force",
    is_flag=True,
    show_default=True,
    envvar="THOTH_BUILD_ANALYSIS_FORCE",
    help="Do not use cached results, always force analysis on the backend.",
)
def cli(
    build_watcher_namespace: str,
    thoth_api_host: str = None,
    verbose: bool = False,
    no_tls_verify: bool = False,
    no_src_registry_tls_verify: bool = False,
    no_dst_registry_tls_verify: bool = False,
    pass_token: bool = False,
    src_registry_user: str = None,
    src_registry_password: str = None,
    dst_registry_user: str = None,
    dst_registry_password: str = None,
    push_registry: str = None,
    analyze_existing: bool = None,
    workers_count: int = None,
    environment_type: str = None,
    debug: bool = False,
    force: bool = False,
):
    """Build watcher bot for analyzing image builds done in cluster."""
    if verbose:
        _LOGGER.setLevel(logging.DEBUG)

    _LOGGER.info("This is build-watcher in version %r", __component_version__)

    _LOGGER.info(
        "Build watcher is watching namespace %r and submitting resulting images to Thoth at %r",
        build_watcher_namespace,
        thoth_api_host,
    )

    # All the images to be processed are submitted onto this queue by producers.
    manager = Manager()
    queue = manager.Queue()

    if analyze_existing:
        # We do this in a standalone process, but reuse worker queue to process images.
        existing_producer = Process(target=_existing_producer, args=(queue, build_watcher_namespace))
        existing_producer.start()

    configuration.explicit_host = thoth_api_host
    configuration.tls_verify = not no_tls_verify
    openshift = OpenShift()

    if not push_registry and (src_registry_password or src_registry_user):
        raise ValueError("Source credentials can be used only if push registry is configured")

    if pass_token:
        if src_registry_password:
            raise ValueError("Flag --pass-token is disjoint with explicit source password propagation")
        src_registry_user = "build-watcher"
        src_registry_password = openshift.token

        if not push_registry and (not dst_registry_user and not dst_registry_password):
            # We do not copy from source, use the source creds for Thoth's analysis.
            dst_registry_user, dst_registry_password = (src_registry_user, src_registry_password)
        elif not dst_registry_user and not dst_registry_password:
            # Reuse credentials if we are in the cluster.
            dst_registry_user = "build-watcher"
            dst_registry_password = openshift.token

    producer = Process(target=_event_producer, args=(queue, build_watcher_namespace))
    producer.start()

    args = [
        queue,
        push_registry,
        environment_type,
        src_registry_user,
        src_registry_password,
        dst_registry_user,
        dst_registry_password,
        no_src_registry_tls_verify,
        no_dst_registry_tls_verify,
        debug,
        force,
    ]
    # We do not use multiprocessing's Pool here as we manage lifecycle of workers on our own. If any fails, give
    # up and report errors.
    process_pool = []
    _LOGGER.info(
        "Starting worker processes, number of workers is set to: %d, environment type of images submitted is %s",
        workers_count,
        environment_type,
    )
    for worker in range(workers_count):
        p = Process(target=_submitter, args=args)
        p.start()
        _LOGGER.info("Started a new worker with PID: %d", p.pid)
        process_pool.append(p)

    # Check if all the processes is still alive.
    while True:
        if any(not process.is_alive() for process in process_pool):
            raise RuntimeError("One of the processes failed")

        time.sleep(5)

    # Always fail, this should be run forever.
    sys.exit(1)


if __name__ == "__main__":
    sys.exit(cli())
