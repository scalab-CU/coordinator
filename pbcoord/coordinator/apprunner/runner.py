'''
Created on Jan 2, 2017

@author: rge
'''
import argparse
import json
import pprint

def parseJsonCfg(jsonCfg):
    with open(jsonCfg) as cfgFile:
        data = json.load(cfgFile)
    return data

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
    
    
    