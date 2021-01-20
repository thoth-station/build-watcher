
## Release 0.7.0 (2021-01-12T22:04:58)
### Features
* :arrow_up: Automatic update of dependencies by kebechet. (#187)
* :arrow_up: Automatic update of dependencies by kebechet. (#185)
* :arrow_up: Automatic update of dependencies by kebechet. (#182)
* Adjustments to use new build analysis endpoint (#183)
* :arrow_up: Automatic update of dependencies by kebechet. (#180)
* update .aicoe.yaml (#179)
* port to python 38 (#176)
* :arrow_up: Automatic update of dependencies by kebechet. (#178)
* :snowman: support pre-commit (#174)
* Remove latest versions limitation (#171)
* Create OWNERS
* added a 'tekton trigger tag_release pipeline issue'
* :pushpin: Automatic dependency re-locking
* Remove latest version restriction from .thoth.yaml
* Update .thoth.yaml
* Catch the manifest exception as warning
* Fixing traceback raise issue with warning
* Remove redundant if statement
*  Fixing @ issue in image push to quay
* Push base image to external registry too
* setup probe on dc as it uses events
* updated playbook with required parameters
* thoth configmap required for build-watcher
* Flexibility to push images to quay
* Happy new year!
* Use RHEL instead of UBI
* Update Thoth configuration file and Thoth's s2i configuration
* updated templates with annotations and param thoth-advise-value
* Propagate deployment name for sentry environment
* openshift deployment templates changed
* Distinguish TLS verification flag
* Start using Thoth's s2i base image
* Added config
* Initial dependency lock
* Stop using extras in thoth-common
* Remove old .thoth.yaml configuration file
* Start using Thoth in OpenShift's s2i
* :bowtie: update few fixes and also prometheus metrics set operation
* :notes: build-watcher is updated to send prometheus metrics
* :tada: update to watch the entire build(images, base_image & buildlog)
* Update zuul pipeline to use the new version trigger build job
* Added a required field for deployment of dc and imagestream in different namespace
* hotfixing webhook url
* Use versions of libraries from PyPI
* Fix logging report
* Report environment type of images submitted for analysis
* Add Thoth's configuration file
* Add Thoth's configuration file
* Propagate environment type on provisioning
* Fix coala issues
* Fix coala issues
* Create service account in deployment
* Provide Ansible playbooks
* Fix coala issues
* State service account configuration in README
* State presence of s2i container
* Fix Coala complains
* Implement process pool of workers
* Add skopeo binary
* Add ability to push containers to an external registry
* Do not share OpenShift instance across namespaces
* using the correct filename convention now
* added std prj cfg
* Introduce event producer following workqueue pattern
* Do not clash with env var used by thoth-common
* State Thamos env var to disable TLS warnings
* Initial bot implementation
### Bug Fixes
* Relock to fix typing extensions issue caused by Pipenv resolver (#191)
* :bug: fixed the webhook url of the build trigger job
* Minor fix for coala
### Improvements
* Provide version identifier for Kebechet and expose it in logs (#190)
* sa and rolebinding creation separated
* Do not run adviser from bc in debug mode
* Distinguish between runtime and buildtime images monitored
* Fixes and improvements during dh-jupyterhub deployment
* Fixes needed for correct pushing
* Add missing parameter, make TLS disabling of warnings parametrizable
* Minor improvements in template
### Automatic Updates
* :pushpin: Automatic update of dependency thamos from 0.10.5 to 0.10.6 (#175)
* :pushpin: Automatic update of dependency thamos from 0.10.5 to 0.10.6 (#173)
* :pushpin: Automatic update of dependency thoth-common from 0.13.8 to 0.14.2 (#172)
* :pushpin: Automatic update of dependency thamos from 0.10.2 to 0.10.5 (#170)
* :pushpin: Automatic update of dependency thoth-common from 0.13.7 to 0.13.8
* :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7
* :pushpin: Automatic update of dependency thamos from 0.10.1 to 0.10.2
* :pushpin: Automatic update of dependency prometheus-client from 0.7.1 to 0.8.0
* :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6
* :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5
* :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
* :pushpin: Automatic update of dependency thamos from 0.10.0 to 0.10.1
* :pushpin: Automatic update of dependency pyyaml from 3.13 to 5.3.1
* :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
* :pushpin: Automatic update of dependency thamos from 0.9.4 to 0.10.0
* :pushpin: Automatic update of dependency thamos from 0.9.3 to 0.9.4
* :pushpin: Automatic update of dependency click from 7.1.1 to 7.1.2
* :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
* :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
* :pushpin: Automatic update of dependency thamos from 0.9.2 to 0.9.3
* :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.9
* :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
* :pushpin: Automatic update of dependency thamos from 0.9.1 to 0.9.2
* :pushpin: Automatic update of dependency thoth-common from 0.12.5 to 0.12.6
* :pushpin: Automatic update of dependency thoth-common from 0.12.4 to 0.12.5
* :pushpin: Automatic update of dependency thamos from 0.9.0 to 0.9.1
* :pushpin: Automatic update of dependency thamos from 0.8.3 to 0.9.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.3 to 0.12.4
* :pushpin: Automatic update of dependency thamos from 0.8.1 to 0.8.3
* :pushpin: Automatic update of dependency pyyaml from 5.3.1 to 3.13
* :pushpin: Automatic update of dependency thoth-common from 0.12.0 to 0.12.3
* :pushpin: Automatic update of dependency thoth-common from 0.10.12 to 0.12.0
* :pushpin: Automatic update of dependency pyyaml from 3.13 to 5.3.1
* :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.10.12
* :pushpin: Automatic update of dependency pyyaml from 5.3 to 3.13
* :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
* :pushpin: Automatic update of dependency thoth-common from 0.10.9 to 0.10.11
* :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
* :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
* :pushpin: Automatic update of dependency thoth-common from 0.10.6 to 0.10.7
* :pushpin: Automatic update of dependency thoth-common from 0.10.5 to 0.10.6
* :pushpin: Automatic update of dependency thoth-common from 0.10.4 to 0.10.5
* :pushpin: Automatic update of dependency thoth-common from 0.10.3 to 0.10.4
* :pushpin: Automatic update of dependency thoth-common from 0.10.2 to 0.10.3
* :pushpin: Automatic update of dependency thamos from 0.8.0 to 0.8.1
* :pushpin: Automatic update of dependency thoth-common from 0.10.1 to 0.10.2
* :pushpin: Automatic update of dependency thoth-common from 0.10.0 to 0.10.1
* :pushpin: Automatic update of dependency thamos from 0.7.7 to 0.8.0
* :pushpin: Automatic update of dependency thoth-common from 0.9.31 to 0.10.0
* :pushpin: Automatic update of dependency thoth-common from 0.9.30 to 0.9.31
* :pushpin: Automatic update of dependency thoth-common from 0.9.29 to 0.9.30
* :pushpin: Automatic update of dependency thoth-common from 0.9.28 to 0.9.29
* :pushpin: Automatic update of dependency thoth-common from 0.9.26 to 0.9.28
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.7 to 0.1.8
* :pushpin: Automatic update of dependency thoth-common from 0.9.25 to 0.9.26
* :pushpin: Automatic update of dependency thoth-common from 0.9.24 to 0.9.25
* :pushpin: Automatic update of dependency thoth-common from 0.9.23 to 0.9.24
* :pushpin: Automatic update of dependency thoth-common from 0.9.22 to 0.9.23
* :pushpin: Automatic update of dependency pyyaml from 5.2 to 5.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.21 to 0.9.22
* :pushpin: Automatic update of dependency thamos from 0.7.6 to 0.7.7
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.6 to 0.1.7
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.5 to 0.1.6
* :pushpin: Automatic update of dependency thoth-common from 0.9.20 to 0.9.21
* :pushpin: Automatic update of dependency thamos from 0.7.5 to 0.7.6
* :pushpin: Automatic update of dependency thoth-common from 0.9.19 to 0.9.20
* :pushpin: Automatic update of dependency thamos from 0.7.4 to 0.7.5
* :pushpin: Automatic update of dependency pyyaml from 5.1.2 to 5.2
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.4 to 0.1.5
* :pushpin: Automatic update of dependency thoth-common from 0.9.17 to 0.9.19
* :pushpin: Automatic update of dependency thoth-common from 0.9.16 to 0.9.17
* :pushpin: Automatic update of dependency thoth-common from 0.9.15 to 0.9.16
* :pushpin: Automatic update of dependency thamos from 0.7.3 to 0.7.4
* :pushpin: Automatic update of dependency thoth-common from 0.9.14 to 0.9.15
* :pushpin: Automatic update of dependency thamos from 0.7.2 to 0.7.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.12 to 0.9.14
* :pushpin: Automatic update of dependency thoth-common from 0.9.11 to 0.9.12
* :pushpin: Automatic update of dependency thoth-common from 0.9.10 to 0.9.11
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.3 to 0.1.4
* :pushpin: Automatic update of dependency thoth-analyzer from 0.1.2 to 0.1.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.9 to 0.9.10
* :pushpin: Automatic update of dependency thoth-common from 0.9.8 to 0.9.9
* :pushpin: Automatic update of dependency thamos from 0.7.0 to 0.7.2
* :pushpin: Automatic update of dependency thoth-common from 0.9.7 to 0.9.8
* :pushpin: Automatic update of dependency thoth-common from 0.9.3 to 0.9.4
* :pushpin: Automatic update of dependency thamos from 0.5.4 to 0.5.5
* :pushpin: Automatic update of dependency thoth-common from 0.9.2 to 0.9.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.1 to 0.9.2
* :pushpin: Automatic update of dependency thamos from 0.5.3 to 0.5.4
* :pushpin: Automatic update of dependency thamos from 0.4.3 to 0.5.3
* :pushpin: Automatic update of dependency thoth-common from 0.9.0 to 0.9.1
* :pushpin: Automatic update of dependency thoth-common from 0.8.11 to 0.9.0
* :pushpin: Automatic update of dependency thamos from 0.4.2 to 0.4.3
* :pushpin: Automatic update of dependency pyyaml from 5.1 to 5.1.1
* :pushpin: Automatic update of dependency thoth-common from 0.8.7 to 0.8.11
* :pushpin: Automatic update of dependency thamos from 0.4.1 to 0.4.2
* :pushpin: Automatic update of dependency thamos from 0.4.0 to 0.4.1
* :pushpin: Automatic update of dependency thoth-common from 0.8.5 to 0.8.7
* :pushpin: Automatic update of dependency thamos from 0.3.1 to 0.4.0
* :pushpin: Automatic update of dependency thoth-common from 0.8.3 to 0.8.5

## Release 0.8.0 (2021-01-20T09:38:40)
### Features
* Do not propagate credentials if user did not request analysis (#219)
* Extend README file with links (#218)
* No submit parameters (#217)
* Adjust deployment templates and README
* Adjust README file and add docs
* Provide parameters to avoid submitting specific inputs (#215)
* Fix typing in the application (#212)
* :arrow_up: Automatic update of dependencies by kebechet. (#216)
* :arrow_up: Automatic update of dependencies by kebechet. (#211)
* Remove Ansible playbooks (#209)
* Add missing template title (#208)
* Add Kebechet issue templates (#206)
* Use s2i-thoth-ubi-8-py38 as a base image (#195)
* Fix logged entries which might be None (#202)
* Add pull-request template (#196)
* Tweak environment variables supplied (#203)
* Fix pre-commit issues and bump black version (#197)
* Fix API version in sources (#199)
* :arrow_up: Automatic update of dependencies by kebechet. (#200)
### Bug Fixes
* Push to registry only if the push registry was provided (#204)
