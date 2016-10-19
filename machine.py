'''
Created on Oct 18, 2016

@author: fengx
'''
import subprocess
import re

from trees import TreeNode

hwloc_line = re.compile('^\s*(\w+)\s+(.*)$')
hwloc_memory = re.compile('\((\d+)([KMG])B\)')

def match_hwloc_line(s):
    m = re.match(hwloc_line, s)
    if m != None:
        return True, m.group(1).lower(), m.group(2)
    else:
        return False, None, None

def match_hwloc_memory(s):
    m = re.match(hwloc_memory, s)
    if m != None:
        size = float(m.group(1))
        unit = m.group(2)
        if unit == 'K':
            size /= 1000
            unit = 'G'
        elif unit == 'M':
            size /= 1000
            unit = 'G'
        return True, size, unit
    return False, 0, 'G' 

def count_leading_whitespace(s):
    i = 0
    for c in s:
        if c.isspace():
            i = i + 1
        else:
            break
    return i
    
def detect_indent_per_level(lines):
    ni = [count_leading_whitespace(l) for l in lines]
    for n in ni:
        if n != 0:
            return n
    return 0

class Machine:
    def __init__(self):
        self.topology = TreeNode('Machine', 0)
    
    def getTopology(self):
        lines = subprocess.check_output(["hwloc-ls"]).split("\n")
        
        curlevel = 0
        nindent = detect_indent_per_level(lines)
        node = self.topology.getLastNodeAtLevl(curlevel)
        
        for line in lines:
            nlevel = count_leading_whitespace(line) / nindent
            if nlevel != curlevel:
                curlevel = nlevel
                node = self.topology.getLastNodeAtLevl(nlevel-1)
            
            idx = 0
            if '+' in line:
                parts = line.split('+')
                print(parts)
                tags = ""
                for p in parts:
                    p = p.strip()
                    atts = p.split(' ')
                    print(atts)
                    if tags == "":
                        tags = tags + atts[0]
                    else:
                        tags = tags + "," + atts[0]
                        
                    if len(atts) >= 2 and atts[1].startswith("L#"):
                        idx = int(atts[1][2:]) 
            else:
                p = line.strip()
                atts = p.split(' ')
                if len(atts) >= 1:
                    tags = atts[0]
                    if len(atts) >= 2 and atts[1].startswith("L#"):
                        idx = int(atts[1][2:]) 
            
            print(tags + ':' + str(idx))

#             ok, k, v = match_hwloc_line(line)
#             print(line)
#             if ok:
#                 if k == 'machine':
#                     ok1, size, unit = match_hwloc_memory(v)
#                     if ok1:
#                         node.attributes['memory'] = (size, unit)
#                 else:
#                     newnode = TreeNode(k, len(node.children))
#                     node.addChild(newnode)
                    
    def show(self):
        print(self.topology)

if __name__ == "__main__":
    m = Machine()
    m.getTopology()
    m.show()
        
        
       
