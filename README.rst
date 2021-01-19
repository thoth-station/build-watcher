Thoth's build-watcher
---------------------

A bot that watches for builds done in an OpenShift cluster and automatically
submits container images and build logs to Thoth. This bot helps Thoth to
aggregate new knowledge about build failures and possible package issues.

See `the demo recording explaining build analysis
<https://www.youtube.com/watch?v=bSkjSU0S5vs>`__ and/or `presentation available
in this repository
<https://github.com/thoth-station/build-watcher/blob/master/docs/pres.pdf>`__.


Build analysis workflow
=======================

.. image:: https://raw.githubusercontent.com/thoth-station/build-watcher/master/pres/wf.png
   :width: 600

If you push images to an external registry, configure bot's credentials to pull
images from the external registry. By default, there will be done
unauthenticated requests on Thoth's User API side.

Note this bot does not directly pull images. Credentials (and token) are
propagated to Thoth's User API.

Also note that Thoth provides cache of image results. It's completely fine if
this bot submits same images for analysis multiple times. Thoth will simply
return correct analysis id from image analysis result cache.

If you build your images in a cluster and would like to submit images for
analysis to Thoth which is running inside another cluster, you can configure
build-watcher to automatically submit images into an external registry
(assuming the in-cluster one has no route exposed) which will then be used as a
source registry for Thoth analysis. See push registry configuration in the help
message.

If you are monitoring a cluster with a lot of builds and pushing images to an
external registry, you can optionally adjust `THOTH_BUILD_WATCHER_WORKERS`
which will cause build-watcher to start a process pool of workers (defaults to
1) where each worker will push image to an external registry (if configured so)
and will submit image for analysis in Thoth. This is handy if pushing to an
external registry takes some time (large images) and/or there is a lot of
builds happening in the cluster (e.g. inspection jobs in Thoth).

Deployment
==========

The build is done using OpenShift's s2i. Templates to deploy this bot are
present in ``openshift/`` directory. See required parameters (and also
commented out parameters in the deployment template) to correctly configure
this bot.

You need to also have present s2i python-36 image based on CentOS 7:

.. code-block:: console

  oc tag --namespace <your-namespace> docker.io/centos/python-36-centos7:latest python-36-centos7:latest

Make sure you assign correct service account to deployment - build-watcher has
to be able to monitor build events in the build-watcher namespace.

Using build-watcher as a CLI
============================

You can also run this bot from your local machine as a CLI. Just make sure you
are logged in into OpenShift cluster (the configuration will be automatically
picked from your acccount) and pass correct values/parameters to CLI:

.. code-block:: console

  $ git clone https://github.com/thoth-station/build-watcher  # or use SSH
  $ cd build-watcher
  $ pipenv install
  $ oc login <cluster>
  $ KUBERNETES_VERIFY_TLS=1 pipenv run python3 app.py --build-watcher-namespace jupyterhub --thoth-api-host khemenu.thoth-station.ninja --no-tls-verify --pass-token --no-registry-tls-verify

See `pipenv run python3 app.py --help` for more info.
