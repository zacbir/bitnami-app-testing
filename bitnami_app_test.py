#!/usr/bin/env python

import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest

def run_unittest_test(path, deployment_directory, deployment_host):
    """
    Run a python unittest in the filesystem context of the deployment directory.
    """

    cur_dir = os.getcwd()
    module = __import__(path, globals(), locals(), ['BitnamiTestCase'], 0)
    suite = unittest.TestLoader().loadTestsFromTestCase(module.BitnamiTestCase)
    os.chdir(deployment_directory)
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.chdir(cur_dir)

def run_casperjs_test(path, deployment_directory, deployment_host):
    """
    Run a CasperJS test.

    For consistency's sake (future-proof for a registry of some sort), we include the deployment directory in the signature, though it is unused.

    We will replace any '{{HOSTNAME}}' instances in the CasperJS file with our deployment_host arg
    """

    with open(path, 'r') as casper_raw:
        casper_script = casper_raw.read()

    casper_script = casper_script.replace('{{HOSTNAME}}', deployment_host)

    handle, actual_casper_script = tempfile.mkstemp(suffix='.js')
    
    with open(actual_casper_script, 'w') as casper_processed:
        casper_processed.write(casper_script)
        
    subprocess.call(['casperjs', 'test', actual_casper_script])

    os.unlink(actual_casper_script)

def main(app, platform, deployment_directory, deployment_host):
    """
    Run a series of tests for an app on a given platform deployed in a particular directory
    """

    identifier = "bitnami-{}-{}".format(platform, app)
    recipe_file_path = "recipes/{}.json".format(identifier)
    
    if not os.path.exists(recipe_file_path):
        print("No recipe found for {}, exiting.".format(identifier))
        sys.exit(1)

    print("Testing {}\n".format(identifier))
        
    with open(recipe_file_path, 'r') as recipe_file:
        recipe = json.load(recipe_file)

    print("Found {} test suite{}\n".format(len(recipe['test_suites']), '' if len(recipe['test_suites']) == 1 else 's'))
        
    for suite in recipe['test_suites']:

        print("{} ({})\n".format(suite['description'], suite['path']))

        if suite['type'] == 'casperjs':
            test_func = run_casperjs_test
        elif suite['type'] == 'unittest':
            test_func = run_unittest_test

        test_func(suite['path'], deployment_directory, deployment_host)
                          
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Test a Bitnami platform app')
    parser.add_argument('-a',
                        dest='app',
                        help='Application identifier (wordpress, &c)',
                        required=True)
    parser.add_argument('-p',
                        dest='platform',
                        help='Platform for the app (docker, &c)',
                        default='docker')
    parser.add_argument('-d',
                        dest='deployment_directory',
                        help='Path to deployment directory',
                        default='.')
    parser.add_argument('-H',
                        dest='hostname',
                        help='The deployment hostname',
                        default='localhost')

    args = parser.parse_args()

    main(app=args.app,
         platform=args.platform,
         deployment_directory=args.deployment_directory,
         deployment_host=args.hostname)

    
