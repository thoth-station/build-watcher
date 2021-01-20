Thoth's build-watcher
---------------------

A bot that watches for builds done in an OpenShift cluster and automatically
submits container images and build logs to Thoth. This bot helps Thoth to
aggregate new knowledge about build failures and possible package issues.

See `the demo recording explaining build analysis
<https://www.youtube.com/watch?v=bSkjSU0S5vs>`__ and/or `presentation available
in this repository
<https://github.com/thoth-station/build-watcher/blob/master/docs/pres.pdf>`__.

.. note::

  Please enable `micropipenv <https://github.com/thoth-station/micropipenv/>`__
  in your OpenShift Source-To-Image builds to make builds verbose and ready
  for data aggregation. micropipenv can be enabled using ``ENABLE_MICROPIPENV=1``
  environment variable in Python 3 UBI/RHEL/CentOS/Fedora container images.
  micropipenv is enabled by default in Thoth based s2i container images and
  the environment variable stated has no effect.

Deploying build-watcher into a namespace
========================================

The build of this bot is done using OpenShift's s2i. OpenShift templates to
deploy this bot are present in ``openshift/`` directory. See required
parameters for configuring this bot.

To deploy this bot, log into your OpenShift cluster:

.. code-block:: console

  oc login <cluster>
  oc project <my-project> # Namespace where the bot should be deployed.

Now you need to setup build-watcher, clone this repo and adjust configuration
in ``deploy.sh`` script.

.. code-block:: console

  git clone https://github.com/thoth-station/build-watcher  # or use SSH
  cd build-watcher
  vim deploy.sh  # Exit using :wq! :)
  # Run the deploy script:
  ./deploy.sh

Removing build-watcher deployment
=================================

To remove build-watcher from a namespace, simply issue:

.. code-block:: console

  oc delete rolebinding,sa,bc,cm,dc,is -l component=thoth-build-watcher

This will clear all the objects created in the cluster related to
build-watcher.

Configuring an external registry
================================

See `presentation available in this repository
<https://github.com/thoth-station/build-watcher/blob/master/docs/pres.pdf>`__
for an architecture scheme.

If you build your images in a cluster and would like to submit images for
analysis to Thoth which is running inside another cluster, you can configure
build-watcher to automatically submit images into an external registry
(assuming the in-cluster one has no external route exposed which would be
accessible to Thoth backend) which will then be used as a source registry for
Thoth analysis. See push registry configuration ``--push-registry``.

Credentials handling
====================

Note this bot does not directly analyze images. Credentials (and possibly
token) are propagated to Thoth's User API which triggers analysis on
backend side.

Caching results on Thoth side
=============================

Thoth provides a cache of build analyses. It's completely fine if this bot
submits same images for analysis multiple times. Thoth will simply return
pre-cached analyses results cache.

Scaling build-watcher
=====================

If you are monitoring a cluster with a lot of builds, you can optionally adjust
``THOTH_BUILD_WATCHER_WORKERS`` which will cause build-watcher to start a
process pool of workers (defaults to 1) where each worker will push image to an
external registry (if configured so) and will submit image for analysis in
Thoth. This is handy if pushing to an external registry takes some time (large
images) and/or there is a lot of builds happening in the cluster.

Using build-watcher as a CLI
============================

You can also run this bot from your local machine as a CLI. Just make sure you
are logged in into OpenShift cluster (the configuration will be automatically
picked from your account) and pass correct values/parameters to the CLI:

.. code-block:: console

  $ git clone https://github.com/thoth-station/build-watcher  # or use SSH
  $ cd build-watcher
  $ pipenv install
  $ oc login <cluster>
  $ KUBERNETES_VERIFY_TLS=1 pipenv run python3 app.py --build-watcher-namespace jupyterhub --thoth-api-host khemenu.thoth-station.ninja --no-tls-verify --pass-token --no-registry-tls-verify

See ``pipenv run python3 app.py --help`` for more info.

Copyright (C) 2020 AICoE `Project Thoth <http://thoth-station.ninja/>`__; Red Hat Inc.
