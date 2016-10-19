#!/usr/bin/env python
import argparse
import subprocess
import time
import sys
import os

from kbase import KBase
from config import Configuration
 
class Launcher:
    def __init__(self, app, size=None, cfgFile=None):
        self.app = app
        self.size = size
        if cfgFile == None:
            self.cfgFile = "default.rc"
        else:
            self.cfgFile = cfgFile
            
        cfg = Configuration()
        if cfgFile != None:
            cfg.loadFromFile(cfgFile)
        
        self.ncores  = cfg.get("ncores", "1")
        self.affinity= cfg.get("affinity")
        self.cpu_pbound = cfg.get("cpu_pbound") 
        self.mem_pbound = cfg.get("mem_pbound")
        
        cfg.saveToFile(self.cfgFile)
    
    def run(self):
        if not os.path.exists(self.app):
            print("Error: could not access application {}".format(self.app))
            sys.exit(-1)
            
        start_time = time.time()
        os.environ["OMP_NUM_THREADS"] = self.ncores
        cmd = []
        cmd.append(self.app)
        p = subprocess.run(cmd)
        end_time = time.time()
        print("{0} {1:8.3f} {2}".format(self.app, end_time - start_time, p.returncode))      
        
    
if __name__ == "__main__":
    print(repr(sys.argv))
    parser = argparse.ArgumentParser(prog="etune-launcher")
    parser.add_argument("-c", "--config_file", help="configuration for launch the application")
    parser.add_argument("-s", "--problem_size", help="problem size")
    parser.add_argument("-p", "--power", help="power bound")
    parser.add_argument("app", help="application path")
    
    args = parser.parse_args()
    
    # load the knowledge database
    kb = KBase()
    kb.dump()
    
    # get the parameters from arguments
    app = args.app
    if args.problem_size == None:
        psize = '-'
    else:
        psize = args.problem_size
    
    if args.power == None:
        power = '-'
    else:
        power = args.power
    
    # read the configuration
    cfgs = kb.get(args.app, psize, power)
    print(cfgs)
    
    # print(args)
    l = Launcher(args.app, args.problem_size, args.config_file)
    #l.run()
    

    
    