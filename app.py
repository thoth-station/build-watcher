#!/usr/bin/env python3
# thoth-build-watcher
# Copyright(C) 2019 Fridolin Pokorny
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

import sys
import logging

import click

from thamos.lib import image_analysis
from thamos.config import config as configuration
from thoth.common import init_logging
from thoth.common import OpenShift


init_logging()

_LOGGER = logging.getLogger("thoth.build_watcher")


@click.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    envvar="THOTH_VERBOSE_BUILD_WATCHER",
    help="Be verbose about what is going on.",
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
    "--no-registry-tls-verify",
    "-R",
    is_flag=True,
    envvar="THOTH_NO_REGISTRY_TLS_VERIFY",
    help="Do not check for TLS certificates when pulling images on Thoth side.",
)
@click.option(
    "--pass-token",
    "-p",
    is_flag=True,
    envvar="THOTH_PASS_TOKEN",
    help="Pass OpenShift token to User API to enable image pulling.",
)
@click.option(
    "--registry-user",
    "-u",
    type=str,
    envvar="THOTH_REGISTRY_USER",
    help="Registry user used to pull images on Thoth User API.",
)
@click.option(
    "--registry-password",
    "-u",
    type=str,
    envvar="THOTH_REGISTRY_PASSWORD",
    help="Registry password used to pull images on Thoth User API.",
)
def cli(
    build_watcher_namespace: str,
    thoth_api_host: str = None,
    verbose: bool = False,
    no_tls_verify: bool = False,
    no_registry_tls_verify: bool = False,
    pass_token: bool = False,
    registry_user: str = None,
    registry_password: str = None,
):
    """Build watcher bot for analyzing image builds done in cluster."""
    if verbose:
        _LOGGER.setLevel(logging.DEBUG)

    _LOGGER.info(
        "Build watcher is watching namespace %r and submitting resulting images to Thoth at %r",
        build_watcher_namespace,
        thoth_api_host,
    )

    openshift = OpenShift()
    v1_build = openshift.ocp_client.resources.get(api_version="v1", kind="Build")
    configuration.explicit_host = thoth_api_host
    configuration.tls_verify = not no_tls_verify

    if pass_token:
        if registry_password:
            raise ValueError(
                "Flag --pass-token is disjoint with explicit password propagation"
            )
        registry_password = openshift.token

    for event in v1_build.watch(namespace=build_watcher_namespace):
        if event["object"].status.phase != "Complete":
            _LOGGER.debug(
                "Ignoring build event for %r - not completed phase %r",
                event["object"].metadata.name,
                event["object"].status.phase,
            )
            continue

        output_reference = event["object"].status.outputDockerImageReference

        try:
            analysis_id = image_analysis(
                image=output_reference,
                registry_user=registry_user,
                registry_password=registry_password,
                verify_tls=not no_registry_tls_verify,
                nowait=True,
            )
            _LOGGER.info(
                "Successfully submitted %r (output reference %r) to Thoth for analysis; analysis id: %s",
                event["object"].metadata.name,
                output_reference,
                analysis_id,
            )
        except Exception as exc:
            _LOGGER.exception(
                "Failed to submit image %r for analysis to Thoth: %s",
                output_reference,
                str(exc),
            )


if __name__ == "__main__":
    sys.exit(cli())
