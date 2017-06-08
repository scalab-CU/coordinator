#!/usr/bin/env python
'''
Created 5 June, 2017

@author: tsranso
'''

import configTrainer
import os


def problem_is_known(appCfg, rscCfg):
    path = get_config_path(appCfg, rscCfg)
    return os.isfile(path)


def write_to_config_file(appCfg, rscCfg, a, d):
    path = get_config_path(appCfg, rscCfg)
    with open(path, 'w') as config_file:
        config = {'a': a, 'd': d}
        config_file.wirte(json.dumps(config))


def get_workload_configuration():
    path = get_config_path(appCfg, rscCfg)

    with open(path, 'r') as config_file:
        json_data = config_file.read()
        data = json_data.loads(json_data)
        return (data['a'], data['d'])


def get_config_path(appCfg, rscCfg):
    return '../{}.json'.format(appCfg['hostname'])


def main():
    if problem_is_known(appCfg, rscCfg):
        return get_workload_configuration(appCfg, rscCfg)
    else:
        (a, d) = recommend_configuration(appCfg, rscCfg)
        write_to_config_file(a, d)
        return (a, d)
