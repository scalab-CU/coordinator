#!/usr/bin/env python
'''
Small testing file to demonstrate the config trainer and selector

@author tsranso
'''

from configSelector import *
from configTrainer import *
import unittest
import json


rsc_file = open('resource1.json', 'r')
rscCfg = json.loads(rsc_file.read())
rsc_file.close()

app_file = open('ep.json', 'r')
appCfg = json.loads(app_file.read())
app_file.close()

#print(json.dumps(appCfg, sort_keys=True, indent=4))

class TestSelectorMethods(unittest.TestCase):

    def test_get_config_path(self):
        self.assertEqual(get_config_path(None), None)
        self.assertEqual(get_config_path({"Bad Dict" : True}), None)
        with open('../apprunner/resource1.json', 'r') as config_file:
            appCfg = json.loads(config_file.read())
            self.assertEqual(get_config_path(appCfg), 'kbase/n01.json')
        
    def test_problem_is_known(self):
        self.assertFalse(problem_is_known(None, None))
        self.assertTrue(problem_is_known(appCfg, rscCfg))

class TestTrainerMethods(unittest.TestCase):

    def test_power_budget_is_sufficient(self):

        self.assertFalse(power_budget_is_sufficient(appCfg,   10))
        self.assertFalse(power_budget_is_sufficient(appCfg,  -10))
        self.assertTrue( power_budget_is_sufficient(appCfg, 1000))

    def test_decide_memory_allocation(self):
        self.assertTrue(False)

    def test_affinity_to_string(self):

        affinity = [[1, 1, 1], [1, 1, 0], [0, 0, 0]]
        self.assertEquals(affinity_to_string(affinity), "0,1,2,3,4")
        affinity = [[0, 0, 0], [0, 1, 1], [1, 1, 1]]
        self.assertEquals(affinity_to_string(affinity), "4,5,6,7,8")
        self.assertEquals(affinity_to_string([]), "")

    def test_determine_critical_power_levels(self):
        determine_critical_power_levels(appCfg)
        
if __name__ == '__main__':
    unittest.main()
