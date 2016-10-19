'''
Created on Oct 18, 2016

@author: fengx
'''
class Machine:
    def __init__(self):
        self.cores=range(24)
        
        self.sockets=[]
        self.sockets.append(self.cores[:12])
        self.sockets.append(self.cores[12:])
        
        self.nummanodes = {0: (64, 'G', self.sockets[0]),  1: (64, 'G', self.sockets[1])}
        
        self.max_power =  500 # in watts
       
