#!/usr/bin/bash

set -x

oc status

THOTH_WATCHED_NAMESPACE="thoth-test-core"  # Namespace where builds are done.
THOTH_INFRA_NAMESPACE="thoth-test-core"  # Namespace where build-watcher container image lives in.
THOTH_LOGGING_NO_JSON="1"  # Do not use structured JSON logging.

# Data submitted to Thoth backend.
THOTH_BUILD_ANALYSIS_NO_BASE_IMAGE="0"  # Do not submit base images used in s2i build.
THOTH_BUILD_ANALYSIS_NO_BUILD_LOG="0"  # Do not submit build logs produced during s2i builds.
THOTH_BUILD_ANALYSIS_NO_OUTPUT_IMAGE="0"  # Do not submit resulting container images produced by s2i.

# Source registry credentials (base container images).
THOTH_SRC_REGISTRY_USER=""
THOTH_SRC_REGISTRY_PASSWORD=""
THOTH_NO_SOURCE_REGISTRY_TLS_VERIFY="1"  # Do not perform TLS verification when pulling images on Thoth side (base container images).
THOTH_PASS_TOKEN=""  # Pass token when communicating with registry.

# Destination registry credentials (resulting container images).
THOTH_DST_REGISTRY_USER=""
THOTH_DST_REGISTRY_PASSWORD=""
THOTH_NO_DESTINATION_REGISTRY_TLS_VERIFY="1"  # Do not perform TLS verification when pulling images on Thoth side (resulting container images).

# Number of workers handling requests.
THOTH_BUILD_WATCHER_WORKERS="1"

# Analyze already present builds found in the namespace.
THOTH_ANALYZE_EXISTING="1"

# Do not change anything below, unless desired.
THOTH_NO_TLS_VERIFY="1"  # Do not perform TLS verification when communicating with Thoth User API.
THOTH_USER_API_HOST="khemenu.thoth-station.ninja"

oc process -f openshift/configmap-template.yaml | oc apply -f -
oc process -f openshift/imageStream-template.yaml | oc apply -f -
oc import-image quay.io/thoth-station/s2i-thoth-ubi8-py38 --confirm -n thoth-test-core
oc process -f openshift/buildConfig-template.yaml | oc apply -f -
oc process -f openshift/service-account-template.yaml -p THOTH_WATCHED_NAMESPACE="$THOTH_WATCHED_NAMESPACE" | oc apply -f -
oc process -f openshift/buildConfig-template.yaml | oc apply -f -
oc start-build thoth-build-watcher
oc process -f openshift/deployment-template.yaml \
  -p THOTH_WATCHED_NAMESPACE="$THOTH_WATCHED_NAMESPACE" \
  -p THOTH_INFRA_NAMESPACE="$THOTH_INFRA_NAMESPACE" \
  -p THOTH_LOGGING_NO_JSON="$THOTH_LOGGING_NO_JSON" \
  -p THOTH_SRC_REGISTRY_USER="$THOTH_SRC_REGISTRY_USER" \
  -p THOTH_SRC_REGISTRY_PASSWORD="$THOTH_SRC_REGISTRY_PASSWORD" \
  -p THOTH_NO_SOURCE_REGISTRY_TLS_VERIFY="$THOTH_NO_SOURCE_REGISTRY_TLS_VERIFY" \
  -p THOTH_PASS_TOKEN="$THOTH_PASS_TOKEN" \
  -p THOTH_DST_REGISTRY_USER="$THOTH_DST_REGISTRY_USER" \
  -p THOTH_DST_REGISTRY_PASSWORD="$THOTH_DST_REGISTRY_PASSWORD" \
  -p THOTH_NO_DESTINATION_REGISTRY_TLS_VERIFY="$THOTH_NO_DESTINATION_REGISTRY_TLS_VERIFY" \
  -p THOTH_BUILD_WATCHER_WORKERS="$THOTH_BUILD_WATCHER_WORKERS" \
  -p THOTH_ANALYZE_EXISTING="$THOTH_ANALYZE_EXISTING" \
  -p THOTH_BUILD_ANALYSIS_NO_BASE_IMAGE="$THOTH_BUILD_ANALYSIS_NO_BASE_IMAGE" \
  -p THOTH_BUILD_ANALYSIS_NO_BUILD_LOG="$THOTH_BUILD_ANALYSIS_NO_BUILD_LOG" \
  -p THOTH_BUILD_ANALYSIS_NO_OUTPUT_IMAGE="$THOTH_BUILD_ANALYSIS_NO_OUTPUT_IMAGE" \
  -p THOTH_NO_TLS_VERIFY="$THOTH_NO_TLS_VERIFY" \
  -p THOTH_USER_API_HOST="$THOTH_USER_API_HOST" | oc apply -f -
