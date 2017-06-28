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

def problem_is_known(appCfg, rscCfg):
    """
    Determines if the problem exists in the kbase.
    appCfg :: dict object from the appRunner, describes application configuration
    rscCfg :: dict from the appRunner, describes resource configuration
    """
    path = get_config_path(appCfg)
    if path is None:
        raise Exception('Kbase not found', '')
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
    path = get_config_path(appCfg)
    with open(path, 'rw') as config_file:
        config = {'a': a, 'd': d}
        kbase = json.loads(config_file.read())

        # Make sure our indicies exist in the kbase
        if not appCfg['app'] in kbase:
            kbase[appCfg['app']] = {}

        if not appCfg['psize'] in kbase[appCfg['app']]:
            kbase[appCfg['app']][appCfg['psize']] = {}

        kbase[appCfg['app']][appCfg['psize']] = config

        config_file.wirte(json.dumps(config))


def get_workload_configuration(appCfg, rscCfg):
    """
    Pulls the configuration out of the kbase, 
    only use after verifying the data exists
    """
    path = get_config_path(appCfg)

    with open(path, 'r') as config_file:
        json_data = json.loads(config_file.read())
        data = json_data[appCfg['app']][appCfg['psize']]
        return (data['a'], data['d'])


def get_config_path(appCfg):
    """
    Arbitrary choice here, I think the hostname will provide the
    smallest number of files to store our knowledge base
    """x
    if appCfg is None or not 'hostname' in appCfg:
        raise Exception('kbase file not found', 'invalid appCfg:{}'.format(appCfg))
        return None
    return 'kbase/{}.json'.format(appCfg['hostname'])


#def main():
def select_config():
    if problem_is_known(appCfg, rscCfg):
        return get_workload_configuration(appCfg, rscCfg)
    else:
        (a, d) = recommend_configuration(appCfg, rscCfg)
        write_to_config_file(a, d)
        return (a, d)
