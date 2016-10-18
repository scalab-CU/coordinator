#!/usr/bin/env python
import argparse
import subprocess
import time
import sys
import os
import re

class Configuration:
    def __init__(self):
        self.configs = {}
    
    def loadFromFile(self, cfgFile):
        with open(cfgFile) as f:
            lines = f.readlines()
        kvRE = re.compile('([\w_]+)\s*=\s*(.+)')
        for line in lines:
            m = re.match(kvRE, line)
            if m:
                k = m.group(1)
                v = m.group(2)
                self.configs[k] = v
            
    def saveToFile(self, cfgFile):
        with open(cfgFile, "w") as f:
            for k in sorted(self.configs.keys()):
                f.write("{}={}\n".format(k, self.configs[k]))
        
    def str(self):
        s = ""
        for k in sorted(self.configs.keys()):
            s += "{}={}\n".format(k, self.configs[k])
        return s

    def get(self, k, v = None):
        if k in self.configs:
            return self.configs[k]
        else:
            self.configs[k] = v
            return v

class KBbase:
    def __init__(self, dbFile="etune.db"):
        self.kbase = {}
        reEntry = re.compile('(\w+):(\w+):(\d+):((\w+)=([^;]);)+')
        with open(dbFile) as f:
            for line in f.readlines():
                m = re.match(reEntry, line)
                if m != None:
                    app = m.group(1)
                    psize = m.group(2)
                    power = m.group(3)
                    for g in range(len(m.group)):
                        print(g)
                    self.kbase[app] = {}
                    self.kbase[app][psize] = {}
                    self.kbase[app][psize][power]={}
                
    def get(self, app, psize, power):
        if app in self.kbase.keys():
            cfg1 = self.kbase[app]
            if psize in cfg1:
                cfg2 = cfg1[psize]
                if power in cfg2:
                    cfgs = cfg2[power]
                    
        return cfgs
                    
    
class Laucher:
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
    parser.add_argument("-c", "--config_file", help="configuration for luanch the application")
    parser.add_argument("-s", "--problem_size", help="problem size")
    parser.add_argument("app", help="application path")
    
    args = parser.parse_args()
    # print(args)
    l = Laucher(args.app, args.problem_size, args.config_file)
    l.run()