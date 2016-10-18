#!/usr/bin/env python
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="etune-launcher")
    parser.add_argument("app", help="application path")
    parser.add_argument("-s", "--problem_size", help="problem size")
    parser.add_argument("-n", "--ncores", type=int, help="number of cores")
    parser.add_argument("-a", "--core_affinity", help="set core affinity")
    parser.add_argument("--cpu_power_bounds", nargs='+', type=int, help="set cpu power bounds")
    parser.add_argument("--mem_power_bounds", nargs='+', type=int, help="set memory power bounds")
    
    args = parser.parse_args()
    print(args)