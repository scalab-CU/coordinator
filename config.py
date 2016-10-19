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