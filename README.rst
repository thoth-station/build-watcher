Thoth's build-watcher
---------------------

Watch for builds done in OpenShift and automatically submit newly built images
to Thoth's image analysis

This is a simple bot that watches for in-cluster build events. If there is a
successful build, build-watcher submits the resulting image to Thoth's analysis endpoint.

The image, tag and registry are obtained from build specification. If you push
images to an internal registry, make sure the bot has ``image-puller`` rights have
``THOTH_PASS_TOKEN`` flag set. The bot will propagate this token to Thoth's User API
which will pull the image for analysis.

If you push images to an external registry, configure bot's credentials to pull
images from the external registry. By default, there will be done
unauthenticated requests on Thoth's User API side.

Note this bot does not directly pull images. Credentials (and token) are
propagated to Thoth's User API.

Also note that Thoth provides cache of image results. It's completely fine if
this bot submits same images for analysis multiple times. Thoth will simply
return correct analysis id from image analysis result cache.

Deployment
==========

The build is done using OpenShift's s2i. Templates to deploy this bot are
present in ``openshift/`` directory. See required parameters (and also
commented out parameters in the deployment template) to correctly configure
this bot.

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
  $ KUBERNETES_VERIFY_TLS=1 pipenv run python3 app.py --build-watcher-namespace jupyterhub --thoth-api-host user-api-thoth.redhat.com --no-tls-verify --pass-token --no-registry-tls-verify

