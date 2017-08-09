#!/usr/bin/env python

import sys
sys.path.append('../')

import configSelector as cs
import configTrainer as ct
import pprint
import unittest
import json

rsc_file = open('../../config/resource1.json', 'r')
rscCfg = json.loads(rsc_file.read())
rsc_file.close()

app_file = open('../../config/ep.json', 'r')
appCfg = json.loads(app_file.read())
app_file.close()

pp = pprint.PrettyPrinter(indent=2)

print("Resource json")
pp.pprint(rscCfg)
print ""
print("App json")
pp.pprint(appCfg)

(a, d) = ct.recommend_configuration(appCfg, rscCfg)
pp.pprint(a)
pp.pprint(d)

def rsum(L):
    if type(L) != list:
        return L
    if L == []:
        return 0
    return rsum(L[0]) + rsum(L[1:])

pp.pprint("Total activated cpus: {}".format(rsum(a)))
pp.pprint("Total cpu power: {}".format(rsum(d['cpu'])))
pp.pprint("Total mem power: {}".format(rsum(d['mem'])))
