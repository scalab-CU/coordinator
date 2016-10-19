import re
import os.path

def parseCfgLine(s, cfgs):
    items = s.split(';')
    kvRE = re.compile("(\w+)\s*=\s*(.+)")
    for item in items:
        if item != '':
            m = re.match(kvRE, item)
            k, v = m.group(1), m.group(2)
            cfgs[k] = v
              
class ConfigLearner:
    def __init__(self, app, psize, pbound):
        self.datafile = "{}-{}-{}.tdat"
        self.training_data = []
        if not os.path.exists(self.datafile):
            with open(self.datafile, "w") as f:
                f.writre("#@etune-config-learner-data\n")
                f.write("#app={} problem_size={} power_bound={}\n".format(app, psize, pbound))
            
        with open(self.datafile) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                
                cfgs = {}
                parseCfgLine(line, cfgs)
                self.training_data.append(cfgs)
    
    def getConfig(self):
        if len(self.training_data) == 0:
            cfg = {}
            self.training_data.append(cfg)
            return cfg
        else:
            cfg = {}
            return cfg
    
class KBase:
    def __init__(self, dbFile="etune.db"):
        self.kbase = {}
        
        self.defaultApp = '-'
        self.defaultPsize = '-'
        self.defaultPBound = '-'
        
        reEntry = re.compile(r'([\w-]+):([\w-]+):([\d-]+):(\w+):(.+)')
        
        with open(dbFile) as f:
            for line in f.readlines():
                m = re.match(reEntry, line)
                if m != None:
                    app = m.group(1)
                    psize = m.group(2)
                    power = m.group(3)
                    mode = m.group(4)
                    cfgLine = m.group(5)
                    
                    if app in self.kbase.keys():
                        cfg1 = self.kbase[app]
                    else:
                        cfg1 = {}
                        self.kbase[app] = cfg1
                    
                    if psize in cfg1.keys():
                        cfg2 = cfg1[psize]
                    else:
                        cfg2 = {}
                        cfg1[psize] = cfg2
                        
                    if power in cfg2.keys():
                        cfg3 = cfg2[power]
                    else:
                        cfg3 = {}
                        cfg2[power] = cfg3
                    cfg3['mode'] = mode
                    
                    parseCfgLine(cfgLine, cfg3)
               
    def get(self, app, psize, power):
        if app in self.kbase.keys():
            cfg1 = self.kbase[app]
        else:
            cfg1 = self.kbase[self.defaultApp]
            
        if psize in cfg1:
            cfg2 = cfg1[psize]
        else:
            cfg2 = cfg1[self.defaultPsize]
        
        if power in cfg2:
            cfgs = cfg2[power]
        else:
            cfgs = cfg2[self.defaultPBound]
                    
        return cfgs
    
    def dump(self):
        for app in self.kbase.keys():
            print("application=" + app)
            cfg1 = self.kbase[app]
            for psize in cfg1.keys():
                print("  size=" + psize)
                cfg2 = cfg1[psize]
                for power in cfg2.keys():
                    print("    power_bound=" + power)
                    cfgs = cfg2[power]
                    for k in cfgs.keys():
                        print("      {}={}".format(k, cfgs[k]))
  
