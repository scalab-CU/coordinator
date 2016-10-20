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
   
class ConfigureRecord:
    def __init__(self, app):
        self.app = app
        self.psize = 1
        self.power = 0
        self.idx = 0
        self.cfgs = {}
        self.projected_perf  = {}
        self.measured_perf = {}
    
class ConfigLearner:
    '''
    ConfigLearner collects and learns optimal configurations for a given problem
    with a given problem size under a given power budget.
    
    ConfigLearner stores the information in a text file which has a format 
    defined as follows:
    Line 1: file type identification]
    Line 2..n: app,psize,power:runid:key1=val1;key2=val2;....:project_perf:actual_perf
    '''
    
    @staticmethod
    def getConfiguration(app, psize, pbound):
        learner = ConfigLearner(app, psize, pbound)
        return learner.getConfg()
        
    def __init__(self, app, psize, pbound):
        self.datafile = "{}.tdat".format(app)
        self.app = app
        self.training_data = []
        if not os.path.exists(self.datafile):
            with open(self.datafile, "w") as f:
                f.write("#@etune-config-learner-data\n")
    
    def readTrainingData(self):
        with open(self.datafile) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                    
                fields = line.split(':')
                if len(fields) != 4:
                    print("warning: wrong format at {0}:{1}".format(self.datafile, line))
                    continue
                else:
                    record = ConfigureRecord(self.app)
                    record_id = fields[0].split(',')
                    record.psize = record_id[1]
                    record.power = record_id[2]
                    
                    parseCfgLine(fields[1], record.cfgs)
                    parseCfgLine(fields[2], record.projected_perf)
                    parseCfgLine(fields[3], record.measured_perf)
                    self.training_data.append(record)
                    
    def writeTrainingData(self):
        with open(self.datafile, "w") as f:
            f.write("#@etune-config-learner-data\n")
            for r in self.training_data:
                f.write(r)
            
    def getConfig(self):
        if len(self.training_data) == 0:
            cfg = {}
            self.training_data.append(cfg)
            return cfg
        else:
            cfg = {}
            return cfg
    
class KBase:
    '''
    KBase implements the Knowledge Base that maps application to runtime configuration
    
    KBase combines with ConfigLearner to locate an optimal or near-optimal 
    runtime cofiguration for an application of specific problem size under a
    given power bound.
    
    The ability of self learning is a key features of this knowledge base. 
    When the knowledge base doesn't have data for an application, it starts 
    the ConfigLearner to learn what configuration would fit this application.
    The knowlegde base will sets the entry for unknown 
    application-problem-power_bound key to a learning state, at which it delegate 
    to the ConfigLearner to serach the optimal configuration.
    '''
    def __init__(self, dbFile="etune.db"):
        '''
        Constructor of KBase
        
        The constructor will read the knowledge base with a datbase file.
        
        At this initial version, we use plain text file to store the knowledge base.
        In the future, we will consider switching to database.
        '''
        self.kbase = {}
        
        self.defaultApp = '-'
        self.defaultPsize = '-'
        self.defaultPBound = '-'
    
    def loadKbaseFromFile(self, dbFile):
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
            cfg1 = {}
            self.kbse[app] = cfg1
            
        if psize in cfg1:
            cfg2 = cfg1[psize]
        else:
            cfg2 = {}
            cfg1[psize] = cfg2
        
        if power in cfg2:
            cfgs = cfg2[power]
        else:
            cfgs = {}
            cfg2[power] = cfgs
        
        if 'mode' not in cfgs:
            cfgs['mode'] = 'L'
        
        if cfgs['mode'] == 'L':
            cfgs = ConfigLearner.getConfiguration(app, psize, power)
            cfg2[power] = cfgs
        
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
  
