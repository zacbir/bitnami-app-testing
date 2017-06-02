# bitnami-app-testing
Experimental testing tool for Bitnami container apps

## Project structure

### bitnami_app_test.py

`bitnami_app_test.py` is a tool for driving the aggregate testing of both unit tests and CasperJS tests for bitnami app deployments. It uses traditional Python unit tests for things like configuration correctness, and CasperJS for testing that web apps are running, properly rendering, and responding to requests. It is run from its checkout, and has its own collection of test recipes, as well as the constituent test definitions, for bitnami apps.

#### Usage

```
usage: bitnami_app_test.py [-h] -a APP [-p PLATFORM] [-d DEPLOYMENT_DIRECTORY]
                           [-H HOSTNAME]

Test a Bitnami platform app

optional arguments:
  -h, --help            show this help message and exit
  -a APP                Application identifier (wordpress, &c)
  -p PLATFORM           Platform for the app (docker, &c)
  -d DEPLOYMENT_DIRECTORY
                        Path to deployment directory
  -H HOSTNAME           The deployment hostname
```

#### Sample output

```
Arthur:bitnami-app-testing zbir
$ python bitnami_app_test.py -a wordpress -p docker -d ../bitnami-docker-wordpress/ -H 192.168.99.100
Testing bitnami-docker-wordpress

Found 2 test suites

Verifying installation configuration (tests.test_bitnami_docker_wordpress)

test_fs_permissions (tests.test_bitnami_docker_wordpress.BitnamiTestCase) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.169s

OK
Verifying installation accepting requests (casperjs/bitnami-docker-wordpress.js)

Test file: /var/folders/6g/tg1z18c97bd92njyfq2b25cr0000gn/T/tmpR8DWJc.js        
# add posts test
PASS Login button exists
PASS Reached login screen
FAIL "li.publish" still did not exist in 5000ms
#    type: uncaughtError
#    file: /var/folders/6g/tg1z18c97bd92njyfq2b25cr0000gn/T/tmpR8DWJc.js
#    error: "li.publish" still did not exist in 5000ms

#    stack: not provided
PASS add posts test
FAIL 3 tests executed in 6.677s, 2 passed, 1 failed, 0 dubious, 0 skipped.      

Details for the 1 failed test:

In /var/folders/6g/tg1z18c97bd92njyfq2b25cr0000gn/T/tmpR8DWJc.js
  add posts test
    uncaughtError: "li.publish" still did not exist in 5000ms
Arthur:bitnami-app-testing zbir
$
```

### recipes

JSON files representing a manifest of test suites to be performed for the apps in question. Identified by the project. In the sample case, `bitnami-docker-wordpress.json` corresponds to the `bitnami-docker-wordpress` app.

The test suites themselves have a description, used in output, a type, and a path to the test suite. Currently, two test suite types are provided for: `unittest` and `casperjs`. `unittest` suites have a dotted path to the Python module, while `casperjs` suites have a filesystem path to the CasperJS file.

### tests

Unit test suites follow normal Python unittest conventions, with one addition, the top level class is called `BitnamiTestCase`. While the individual test module could be run independently, it is intended to be imported on its own in the course of running `bitnami_app_test.py`.

### casperjs

CasperJS test suites operate via normal HTTP boundaries, but have no notion of the specifics of an app deployment, so are written with placeholders, like `{{HOSTNAME}}`, which our test runner will manipulate and substitute with the appropriate value, passed in as a command line argument.

## Assumptions

  - Dependencies are already installed and the app in question has already been deployed. In this case, `VirtualBox`, `docker`, `CasperJS`, and the `bitnami-docker-wordpress` app.

  - For test suite recipes, we're assuming that all testable targets are consistently named `bitnami-{deployment platform}-{app name}`.

  - Unit tests for apps may require resources pertinent to the deployment path of the app under test, so we change our working directory to the `deployment_path` for the duration of the unit test run. CasperJS tests, testing the specific host directly, have no such constraints.

## TODO

  - Rather than colocate all the recipes and tests (both unittest and CasperJS) with the tool, I'd provide a service where they could be looked up, freeing the need to deploy a new version every time new tests are created/updated.

  - Rather than simple, one-off functions handling the two types of tests, I'd establish a richer class hierarchy that had more internal smarts for getting pertinent information from the environment to satisfy internal state. For instance, while Docker provides environment variables, and presumably other deployment tools do as well, I hoisted the hostname of the Docker deployment as a command line argument.

  - Rather than a chain of `if/elif` tests, a registry to look up the appropriate per-test tool.

  - Currently, we serially perform unit tests and then CasperJS tests, each siloed. Adapting either or both to a common set of test metadata would allow for a single output presentation for consistency and better analysis (aggregated tests run, aggregated successes and failures, &c). Perhaps using a common output style like Xunit, which would also then be ready for consumption by popular continuous integration tools.

  - Provide for direct installation of the app in question, with appropriate cleanup afterwards. Currently, we only test deployed apps, and there is a non-zero chance that tests run (particularly anything that exercises the app) will leave behind unwanted persistent data.