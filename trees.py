'''
Created on Oct 19, 2016

@author: xizhouf
'''

class TreeNode(object):
    '''
    Tree Data Structure 
    '''
    def __init__(self, tag, idx):
        '''
        Constructor
        '''
        self.tag = tag
        self.idx = idx
        self.children = []
        self.parent = None
        self.attributes = {}
    
    def addChild(self, node):
        '''
        add a child node
        '''
        self.children.append(node)
        node.parent = self
    
    def toString(self, l):
        s = l * ' ' + "{0}:{1}:{2}".format(self.tag, self.idx, self.attributes)
        for c in self.children:
            s += '\n' + c.toString(l + 1)
        return s
    
    def __str__(self):
        return self.toString(0)
    
    def getLastNodeAtLevel(self, level):
        node = self
        l = 0
        while l < level:
            if len(node.children) > 0:
                node = node.children[-1]
            else:
                node = None
                break
            l = l + 1
        return node
    
    def buildTagMapHelper(self, m):
        tags = self.tag.split(',')
        for tag in tags:
            if tag in m:
                lst = m[tag]
                lst.append(self)
            else:
                lst = [self]
                m[tag] = lst
        for c in self.children:
            c.buildTagMapHelper(m)
    
    def buildTagMap(self):
        m = {}
        self.buildTagMapHelper(m)
        return m
    