#!/usr/bin/env python
"""
Configuration Selector for the coordinator software system.
This file interfaces with the runner.py in the apprunner directory
to suggest a power configuration for a problem size to an application 
on a machine. Configuration consists of a processor affinity map and a
power distribution vector.

Created 5 June, 2017

@author: tsranso
"""

import configTrainer
import json
import os.path

def problem_is_known(appCfg, rscCfg):
    """
    Determines if the problem exists in the kbase.
    appCfg :: dict object from the appRunner, describes application configuration
    rscCfg :: dict from the appRunner, describes resource configuration
    """
    path = get_config_path(rscCfg, appCfg)
    if path is None or not os.path.isfile(path):
        #raise Exception('Kbase not found', '')
        return False # Bonk out if there is no kbase file
    with open(path, 'r') as config_file:
        kbase = json.loads(config_file.read())
        return appCfg['app'] in kbase and appCfg['psize'] in kbase[appCfg['app']]
    return false  # just default to false for safety


def write_to_config_file(appCfg, rscCfg, a, d):
    """
    Writes the configuration to the appropriate kbase database file
    a :: affinity map from configTrainer
    d :: power distribution, also from configTrainer
    """

    path = get_config_path(rscCfg, appCfg)

    if not os.path.isfile(path):
        with open(path, 'w+') as config_file:
            config = {appCfg['app'] : {appCfg['psize'] : {'a': a, 'd': d}}}
            config_file.write(json.dumps(config, indent=2, sort_keys=True))
    else:
        with open(path, 'r+') as config_file:
            config = {'a': a, 'd': d}
            kbase = json.loads(config_file.read())

            if appCfg['app'] in kbase:
                if appCfg['psize'] in kbase[appCfg['app']]:
                    return
            
            # Make sure our indicies exist in the kbase
            if not appCfg['app'] in kbase:
                kbase[appCfg['app']] = {}

            if not appCfg['psize'] in kbase[appCfg['app']]:
                kbase[appCfg['app']][appCfg['psize']] = {}

            kbase[appCfg['app']][appCfg['psize']] = config

            config_file.write(json.dumps(config, indent=2, sort_keys=True))


def get_workload_configuration(appCfg, rscCfg):
    """
    Pulls the configuration out of the kbase, 
    only use after verifying the data exists
    """
    path = get_config_path(rscCfg, appCfg)

    with open(path, 'r') as config_file:
        json_data = json.loads(config_file.read())
        data = json_data[appCfg['app']][appCfg['psize']]
        return (data['a'], data['d'])


def get_config_path(rscCfg, appCfg):
    """
    Arbitrary choice here, I think the hostname will provide the
    smallest number of files to store our knowledge base
    """
    if rscCfg is None or not 'hostname' in rscCfg:
        #raise Exception('kbase file not found')
        #print(rscCfg)
        return None
    return '../kbase/{}.json'.format(rscCfg['hostname'])


def select_config(appCfg, rscCfg):
    if problem_is_known(appCfg, rscCfg) and False:
        print "Problem is known"
        return get_workload_configuration(appCfg, rscCfg)
    else:
        print "Problem not known, recommending configuration"
        (a, d) = configTrainer.recommend_configuration(appCfg, rscCfg)
        write_to_config_file(appCfg, rscCfg, a, d)
        return (a, d)
