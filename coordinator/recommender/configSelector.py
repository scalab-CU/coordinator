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

import subprocess
import time
import configTrainer as ct
import json
import os.path
from math import floor
from string import replace

def problem_is_known(appCfg, rscCfg):
    """
    Determines if the problem exists in the kbase.
    appCfg :: dict object from the appRunner, describes application configuration
    rscCfg :: dict from the appRunner, describes resource configuration
    """
    path = get_problem_config_path()
    if path is None or not os.path.isfile(path):
        #raise Exception('Kbase not found', '')
        return False # Bonk out if there is no kbase file
    with open(path, 'r') as config_file:
        kbase = json.loads(config_file.read())
        return appCfg['app'] in kbase and appCfg['psize'] in kbase[appCfg['app']]
    return false  # just default to false for safety

def median(L):
    if len(L) == 1:
        return floor(L[0])
    if len(L) == 2:
        return floor((L[0] + L[1]) / 2)
    return median(L[1:-1])

def determine_base_power_levels(rscCfg):

    print "Determining base power levels"
    
    rapl_resolution = 0.1
    rapl_location = rscCfg['rapl_reader_location']
    rapl_filename = "/tmp/base_power.log"

    # we want the power of the entire socket, even if only running on one core
    rapl_command = ['sudo', rapl_location + '/rapl', '-s', str(rapl_resolution), '-c', '0,12', '-f', rapl_filename]
    rapl_pid = subprocess.Popen(rapl_command, stdout=subprocess.PIPE).pid
    time.sleep(5)
    subprocess.call(['sudo', 'kill', str(rapl_pid)])
    
    cpu_powers = []
    mem_powers = []
        
    with open(rapl_filename, 'r') as rapl_log:
        next(rapl_log) # jump over the header line
        for line in rapl_log:
            line = ' '.join(line.split())
            line = line.split()
            cpu_powers.append(float(line[2]))
            cpu_powers.append(float(line[6]))
            mem_powers.append(float(line[4]))
            mem_powers.append(float(line[8]))

    #subprocess.call(['sudo', 'rm', '-f', rapl_filename])
    
    # chop off the ends for rapl reading inconsistencies
    return (median(mem_powers[5:-5]), median(cpu_powers[5:-5]))


def write_problem_config_file(appCfg, rscCfg, a, d):
    """
    Writes the configuration to the appropriate kbase database file
    a :: affinity map from configTrainer
    d :: power distribution, also from configTrainer
    """

    problem_path = get_problem_config_path()
    power_levels_path = get_power_config_path()

    if not os.path.isfile(problem_path):
        with open(problem_path, 'w+') as problem_config_file:
            config = {appCfg['app'] : {appCfg['psize'] : {'a': a, 'd': d}}}
            problem_config_file.write(json.dumps(config, indent=2, sort_keys=True))
    else:
        with open(problem_path, 'w+') as problem_config_file:
            config = {'a': a, 'd': d}
            kbase = json.loads(problem_config_file.read())

            if appCfg['app'] in kbase:
                if appCfg['psize'] in kbase[appCfg['app']]:
                    return
            
            # Make sure our indicies exist in the kbase
            if not appCfg['app'] in kbase:
                kbase[appCfg['app']] = {}

            if not appCfg['psize'] in kbase[appCfg['app']]:
                kbase[appCfg['app']][appCfg['psize']] = {}

            kbase[appCfg['app']][appCfg['psize']] = config
            problem_config_file.write(json.dumps(config, indent=2, sort_keys=True))

def get_workload_configuration(appCfg, rscCfg):
    """
    Pulls the configuration out of the kbase, 
    only use after verifying the data exists
    """
    path = get_problem_config_path()

    with open(path, 'r') as config_file:
        json_data = json.loads(config_file.read())
        data = json_data[appCfg['app']][appCfg['psize']]
        return (data['a'], data['d'])

def get_power_config_path():
    return replace(get_problem_config_path(), 'problems.json', 'power.json')

def get_problem_config_path():
    """
    Arbitrary choice here, I think the hostname will provide the
    smallest number of files to store our knowledge base
    """
    hostname = subprocess.check_output(['hostname'], shell=True).strip()
    return '../kbase/{}.problems.json'.format(hostname)

def ensure_power_level_files(appCfg, rscCfg):

    path = get_power_config_path()
    
    if not os.path.isfile(path):
        with open(path, 'w+') as power_config_file:
            (base_mem, base_cpu) = determine_base_power_levels(rscCfg)
            critical_power_levels = ct.determine_critical_power_levels(appCfg, rscCfg)
            config = {"base_power_levels" : {"cpu" : base_cpu, "mem" : base_mem}, "critical_power_levels" : critical_power_levels}
            power_config_file.write(json.dumps(config, indent=2, sort_keys=True))
            print "Wrote power levels to knowledge base"
    else:
        with open(path, 'w+') as power_config_file:
            powers = json.loads(power_config_file.read())
            if not 'critical_power_levels' in powers:
                powers['critical_power_levels'] = ct.determine_critical_power_levels(appCfg, rscCfg)
            if not 'base_power_levels' in powers:
                powers['base_power_levels'] = determine_base_power_levels(rscCfg)
            power_config_file.write(json.dumps(powers, indent=2, sort_keys=True))

def get_power_cfg():
    with open(get_power_config_path(), 'r') as power_config:
        powerCfg = json.loads(power_config.read())
    return powerCfg
    

def select_config(appCfg, rscCfg):
    if problem_is_known(appCfg, rscCfg):
        print "Problem is known"
        return get_workload_configuration(appCfg, rscCfg)
    else:
        print "Problem not known, recommending configuration"
        ensure_power_level_files(appCfg, rscCfg)
        (a, d) = ct.recommend_configuration(appCfg, rscCfg, get_power_cfg())
        write_problem_config_file(appCfg, rscCfg, a, d)
        return (a, d)
