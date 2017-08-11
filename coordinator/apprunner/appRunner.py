#!/usr/bin/env python
'''
Created on Jan 2, 2017

@authors: rge, tsranso
'''
import argparse
import json
import pprint
import subprocess
import sys
import jobWrapper

sys.path.append('../')
from recommender import configSelector

#from astroid.tests import resources

def parseJsonCfg(jsonCfg):
    with open(jsonCfg) as cfgFile:
        data = json.load(cfgFile)
    return data


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="run application under power bound")
    p.add_argument('app_cfg')
    p.add_argument('resource_cfg')
    p.add_argument('submit_job')
    args = p.parse_args()
    print(args)
    
    appCfg = parseJsonCfg(args.app_cfg)
    rscCfg = parseJsonCfg(args.resource_cfg)
    submit_job = False
    if args.submit_job in ["True", "true", "t"]:
        submit_job = True
        
    # pprint.pprint(appCfg)
    # pprint.pprint(rscCfg)

    (a, d) = configSelector.select_config(appCfg, rscCfg)
    
    jobWrapper.make_wrapper(appCfg, rscCfg, configSelector.get_power_cfg(), a, d)

    if submit_job:
        subprocess.call(["qsub", "{}.job".format(appCfg["app"])])
