#!/usr/bin/env python
'''
Small testing file to demonstrate the config trainer and selector

@author tsranso
'''

from configSelector import *
import unittest
import json

class TestSelectorMethods(unittest.TestCase):

    def test_get_config_path(self):
        self.assertEqual(get_config_path(None), None)
        self.assertEqual(get_config_path({"Bad Dict" : True}), None)
        with open('../apprunner/resource1.json', 'r') as config_file:
            appCfg = json.loads(config_file.read())
            self.assertEqual(get_config_path(appCfg), 'kbase/n01.json')
        
    def test_problem_is_known(self):
        self.assertFalse(problem_is_known(None, None))

        app_file = open('../apprunner/resource1.json', 'r')
        appCfg = json.loads(app_file.read())
        app_file.close()

        rsc_file = open('../apprunner/ep.json', 'r')
        rscCfg = json.loads(rsc_file.read())
        rsc_file.close()

        self.assertTrue(problem_is_known(appCfg, rscCfg))

class TestTrainerMethods(unittest.TestCase):

    def test_power_budget_is_sufficient(self):
        app_file = open('../apprunner/resource1.json', 'r')
        appCfg = json.loads(app_file.read())
        app_file.close()

        self.assertFalse(power_budget_is_sufficient(appCfg, 10))
        self.assertFalse(power_budget_is_sufficient(appCfg, -10))
        self.assertTrue(power_budget_is_sufficient(appCfg, 1000))

        
if __name__ == '__main__':
    
    unittest.main()
