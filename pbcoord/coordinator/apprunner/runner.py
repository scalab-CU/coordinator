#!/usr/bin/env python
'''
Created on Jan 2, 2017

@author: rge
'''
import argparse
import json
import pprint
import subprocess
import sys
from string import Template
from astroid.tests import resources

def parseJsonCfg(jsonCfg):
    with open(jsonCfg) as cfgFile:
        data = json.load(cfgFile)
    return data

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

def listToString(lst):
    s = ''
    for e in lst:
        if s == '':
            s = '{}'.format(e)
        else:
            s = s + ",{}".format(e)
    return s

def getHWResources(appCfg, rscCfg):
    resources = ''
    if appCfg['program_model'] == 'omp':
        resources = 'export OMP_NUM_THREADS={}\nexport GOMP_CPU_AFFINITY=\"{}\"'.format(rscCfg['num_threads'], listToString(rscCfg['cpu_affinity']))
    return resources   
      
def runApp(appCfg, rscCfg):
    script = "{}.job".format(appCfg["app"])
    tmpl = Template("""#!/bin/bash

$wms_preample

# Set Power Bounds
$set_power_bound

# Set CPU affinity
$set_resource

# Run the binary
$exec_task
""")
    wms_preample = "#PBS -l nodes={}\n".format(rscCfg["hostname"])
    set_resources = getHWResources(appCfg, rscCfg)
    set_power_bound = getPowerSetting(rscCfg)
    exec_task = "{}\n".format(appCfg["path"])
    
    with open(script, "w") as f:
        f.write(tmpl.substitute(wms_preample=wms_preample, 
                                set_resource=set_resources, 
                                set_power_bound=set_power_bound, 
                                exec_task=exec_task))
    
    #subprocess.call(["qsub", script])
    with open(script) as f:
        for line in f.readlines():
            sys.stdout.write(line)
            
            
    
if __name__ == '__main__':
    p = argparse.ArgumentParser(description="run application under power bound")
    p.add_argument('app_cfg')
    p.add_argument('resource_cfg')
    args = p.parse_args()
    print(args)
    
    appCfg = parseJsonCfg(args.app_cfg)
    rscCfg = parseJsonCfg(args.resource_cfg)
    pprint.pprint(appCfg)
    pprint.pprint(rscCfg)
    
    runApp(appCfg, rscCfg)
    
    
    