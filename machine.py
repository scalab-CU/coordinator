'''
Created on Oct 18, 2016

@author: fengx
'''
import subprocess
import re
import sys
from trees import TreeNode

hwloc_line = re.compile('^\s*(\w+)\s+(.*)$')
hwloc_memory = re.compile('\((\d+)([KMG])B')

def matchHwlocLline(s):
    m = re.match(hwloc_line, s)
    if m != None:
        return True, m.group(1).lower(), m.group(2)
    else:
        return False, None, None

def matchHwlocMemory(s):
    m = re.match(hwloc_memory, s)
    if m != None:
        size = int(m.group(1))
        unit = m.group(2)
        return True, size, unit
    return False, 0, 'G' 

def countLeadingWhitespace(s):
    i = 0
    for c in s:
        if c.isspace():
            i = i + 1
        else:
            break
    return i
    
def detectIndentPerLevel(lines):
    ni = [countLeadingWhitespace(l) for l in lines]
    for n in ni:
        if n != 0:
            return n
    return 0

class Machine:
    def __init__(self):
        self.topology = TreeNode('Machine', 0)
        self.getTopology()
        self.tagMap = self.topology.buildTagMap()
        self.cores = self.tagMap['Core']
  
    def getTopology(self):
        lines = subprocess.check_output(["hwloc-ls"]).split("\n")
        #lines = subprocess.check_output(["ssh", "fengx@ivy2.cs.clemson.edu", "hwloc-ls"]).split("\n")
        
        curlevel = 0
        nindent = detectIndentPerLevel(lines)
        node = self.topology.getLastNodeAtLevel(curlevel)
        
        for line in lines:
            nlevel = countLeadingWhitespace(line) / nindent
            line = line.strip()
            if len(line) == 0:
                continue
                
            if nlevel != curlevel:
                curlevel = nlevel
                node = self.topology.getLastNodeAtLevel(nlevel-1)
            
            idx = 0
            if '+' in line:
                parts = line.split('+')
                #print(parts)
                tags = ""
                for p in parts:
                    p = p.strip()
                    atts = p.split(' ')
                    #print(atts)
                    if tags == "":
                        tags = tags + atts[0]
                    else:
                        tags = tags + "," + atts[0]
                        
                    if len(atts) >= 2 and atts[1].startswith("L#"):
                        idx = int(atts[1][2:])
                newnode = TreeNode(tags, idx)
                for p in parts:
                    p = p.strip()
                    atts = p.split(' ')
                    if len(atts) >= 3 and atts[2].startswith("("):
                        ok, memsize, memunit = matchHwlocMemory(atts[2])
                        if ok:
                            newnode.attributes[atts[0]] = (memsize, memunit)
                node.addChild(newnode)
            else:
                p = line.strip()
                atts = p.split(' ')
                if len(atts) >= 1:
                    tags = atts[0]
                    if len(atts) >= 2 and atts[1].startswith("L#"):
                        idx = int(atts[1][2:])
                    
                    if tags.lower() == 'machine' and atts[1].startswith("("):
                        ok, memsize, memunit = matchHwlocMemory(atts[1])
                        if ok:
                            node.attributes[atts[0]] = (memsize, memunit)
                    else:
                        newnode = TreeNode(tags, idx)
                        if len(atts) >= 3 and atts[2].startswith("("):
                            ok, memsize, memunit = matchHwlocMemory(atts[2])
                            if ok:
                                newnode.attributes[atts[0]] = (memsize, memunit)
                    
                        node.addChild(newnode)
    
    def show(self):
        print(self.topology)
        for c in self.cores:
            print(c.tag, c.idx, c.attributes)
        for t in self.tagMap.keys():
            sys.stdout.write(t + ': ')
            for n in self.tagMap[t]:
                sys.stdout.write(str(n.idx) + ' ')
            sys.stdout.write('\n')
            sys.stdout.flush()

if __name__ == "__main__":
    m = Machine()
    m.getTopology()
    m.show()