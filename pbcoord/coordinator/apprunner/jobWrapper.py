#!/usr/bin/env python

import argparse
import json
import pprint
import subprocess
import sys
from string import Template

def getPowerSetting(rscCfg):
    if 'power_allocation' in rscCfg.keys():
        power_setting = "/usr/local/bin/pbset"
        pwr_setting = rscCfg['power_allocation']
        if 'cpu' in pwr_setting.keys():
            socket_pwrs = pwr_setting['cpu']['sockets']
            s = ''
            psum = 0
            for k in sorted(socket_pwrs.keys()):
                v = socket_pwrs[k]
                psum = psum + v
                if s == '':
                    s = '--pkg {}:{}'.format(k, v)
                else:
                    s = s + ',{}:{}'.format(k, v)
            if psum != pwr_setting['cpu']['total']:
                sys.stderr.write("incorrect power setting: total power does not equal to the sum of socket power\n")
                sys.exit(1)
                
            if s != '':
                power_setting = power_setting + ' ' + s
                
        if 'mem' in pwr_setting.keys():
            socket_pwrs = pwr_setting['mem']['modules']
            s = ''
            psum = 0
            for k in sorted(socket_pwrs.keys()):
                v = socket_pwrs[k]
                psum = psum + v
                if s == '':
                    s = '--dram {}:{}'.format(k, v)
                else:
                    s = s + ',{}:{}'.format(k, v)
            if psum != pwr_setting['mem']['total']:
                sys.stderr.write("incorrect power setting: total power does not equal to the sum of socket power\n")
                sys.exit(1)

            if s != '':
                power_setting = power_setting + ' ' + s
        return power_setting
    else:
        return ''

def getHWResources(appCfg, rscCfg):
    resources = ''
    if appCfg['program_model'] == 'omp':
        resources = 'export OMP_NUM_THREADS={}\nexport GOMP_CPU_AFFINITY=\"{}\"'.format(rscCfg['num_threads'], listToString(rscCfg['cpu_affinity']))
    return resources


def listToString(lst):
    s = ''
    for e in lst:
        if s == '':
            s = '{}'.format(e)
        else:
            s = s + ",{}".format(e)
    return s   

def affinity_to_string(affinity):
    """
    Convert the affinity array to a string to be passed into taskset in time_process_with_affinity
    affinity :: Affinity array

    returns a string
      ex : [[1, 1, 1], [1, 1, 0], [0, 0, 0]] = '1,2,3,4,5'
    """

    if affinity is None or affinity == []:
        return ""
    flat_affinity = [item for sublist in affinity for item in sublist]
    
    # pick out all the cores that are active and associate their indicies
    # and shove all their indices into 
    cores = zip(*filter(lambda x : x[1] == 1, enumerate(flat_affinity)))[0]

    return ','.join(str(core) for core in cores)

def make_taskset_command(a, appCfg):
    
   return 'taskset -c ' + affinity_to_string(a) + " " + appCfg['path'] 

def make_pb_command(d):
    comm = "/usr/local/bin/pbset --pkg"
    for i in range(len(d['cpu'])):
        comm += str(i) + ":" + str(sum(d['cpu'][i])) + ","
    comm = comm[:-1]
    comm += " --dram "
    for i in range(len(d['mem'])):
        comm += str(i) + ":" + str(sum(d['mem'])) + ","
    comm = comm[:-1]
    comm += "\n"
    return comm

def make_wrapper(appCfg, rscCfg, a, d):
    script = "{}.job".format(appCfg["app"])
    tmpl = Template("""#!/bin/bash

$wms_preample

# Set Power Bounds
$set_power_bound

# Run the binary
$exec_task
""")
    wms_preample = "#PBS -l nodes={}\n".format(rscCfg["hostname"])
    set_resources = getHWResources(appCfg, rscCfg)
    #set_power_bound = getPowerSetting(rscCfg)
    #exec_task = "{}\n".format(appCfg["path"])
    set_power_bound=make_pb_command(d)
    exec_task=make_taskset_command(a, appCfg)
    
    with open(script, "w") as f:
        f.write(tmpl.substitute(wms_preample=wms_preample, 
                                set_power_bound=make_pb_command(d), 
                                exec_task=make_taskset_command(a, appCfg)))
    print("Wrapper template filled")
    # with open(script) as f:
    #     for line in f.readlines():
    #         sys.stdout.write(line)
