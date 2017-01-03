'''
Created on Jan 2, 2017

@author: rge
'''
import argparse
import json
import pprint
import subprocess

def parseJsonCfg(jsonCfg):
    with open(jsonCfg) as cfgFile:
        data = json.load(cfgFile)
    return data

def runApp(appCfg, rscCfg):
    script = "{}.job".format(appCfg["app"])
    with open(script, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("#PBS -l nodes={}\n\n".format(rscCfg["hostname"]))
        f.write("export OMP_NUM_THREADS={}\n".format(rscCfg["num_cores"]))
        f.write("{}\n".format(appCfg["path"]))
    
    subprocess.call(["qsub", script])
    

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
    
    
    