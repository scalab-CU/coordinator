#!/usr/bin/env python
'''
Created on May 31, 2017

@author: tsranso

** Summary

Implementation of the configuration trainer outlined in Section V.B. of 
Application-Aware Power Coordination on Power Bounded NUMA Multicore Systems, Ge et al

Used mostly in conjunction with configSelector in order to recomend a configuration 
to the user
'''

from functools import reduce
import json
import datetime

## Global variales yay python scripting
M = 4 # cores per processor
N = 2 # number of processors
# Affinity map, 1 if that core is active, 0 otherwise
a = [[0 for m in range(M)] for n in range(N)]
# Power distribution vector
d = dict()
d["cpu"] = [[0 for m in range(M)] for n in range(N)]
d["mem"] =  [0 for n in range(N)]
# Critical power levels, filled in by script
P = dict()
P["cpu"] = [0, 0, 0, 0]
P["mem"] = [0, 0]

def power_budget_is_sufficient(appCfg, Pb):
    """
    Determine if there is enough power being supplied to continue with algorithm
    Pb :: Power Budget
    """
    if (Pb > P["cpu"][1] + P["mem"][1]):
        # Allocate max memory to all memory nodes
        single_memory_allocation = P["mem"][1] / N
        d["mem"] = [single_memory_allocation for k in range(N)]
        # Set thread concurrency and affinity from pivot execution configuration
        read_pivot_config()
        return True

    elif (Pb > P["cpu"][4] + P["mem"][2]):
        decide_memory_allocation(appCfg, Pb)
        return True

    if (Pb < P["cpu"][4] + P["mem"][2]):
        # "power budget too low"
        return False


def decide_memory_allocation(appCfg, Pb):
    """
    How is the power allocated to the memory?
    Pb :: Power Budget
    """
    #if (Pb > P["cpu"][2] + P["mem"][1]):
    single_memory_allocation = P["mem"][1] / N
    d["mem"] = [single_memory_allocation for k in range(N)]
    decide_core_allocation(appCfg, Pb - P["mem"][1])


def update_indicies(socket_index, core_index):
    """
    Utility function to correctly increment indicies for the decide_core_allocation method
    socket_index :: current socket index
    core_idex :: current core index
    """
    core_index += 1
    # Number of cores per processor
    if core_index == M:
        core_index = 0
        socket_index += 1
    # Number of sockets
    if socket_index == N:
        core_index = 0
        socket_index = 0
    return (socket_index, core_index)


def decide_core_allocation(appCfg, Pb):
    """
    Determine the power allocated to the cores, store the data in the d array

    appCfg :: dict from appRunner, tells us the scalability here
    Pb :: Power Budget
    """
    if (appCfg["scalability"] == "high"):

        socket_index = 0
        core_inedx = 0
        # Give power to as many cores as we can
        while Pb >= P["cpu"][4]:
            d["cpu"][socket_index][core_index] = P["cpu"][4]
            Pb -= P["cpu"][4]
            (socket_index, core_index) = update_indicies(socket_index,
                                                         core_index)
        # and upgrade the power as the budget allows
        while (Pb >= P["cpu"][3]):
            d["cpu"][socket_index][core_inedx] = P["cpu"][3]
            (socket_index, core_inedx) = update_indicies(socket_index,
                                                         core_inedx)
            # Because the memory is already set to L3, just take off the difference
            Pb -= (P["cpu"][3] - P["cpu"][4])
    # Purposefully not inverting this logic
    #   (loops inside ifs instead of ifs inside loops) for readability and to
    #   more closely follow the paper specification
    elif (appCfg["scalability"] == "low"):
        # Give max power available to all the activated cores
        for socket_index in range(d["cpu"]):
            for core_index in range(socket_index):
                if (Pb >= P["cpu"][3]):
                    d["cpu"][socket_index][core_index] = P["cpu"][3]
                    Pb -= P["cpu"][3]
                elif (Pb >= P["cpu"][4]):
                    d["cpu"][socket_index][core_index] = P["cpu"][4]
                    Pb -= P["cpu"][4]
    # at this point we know that the application scalability is moderate
    # TODO: this
    #else:
    #    return
    decide_core_affinity(appCfg)


def decide_core_affinity(appCfg):
    """
    Edit the core affinity array (a) in accordance to the memory access intensity
    """
    if (appCfg["memory_intensity"] == "high"):
        # Decide between high core clustering or more spread out
        a = high_memory_intensity()
    else:
        # Pack as many activated cores into the fewest sockets
        for index in range(sum(reduce(list.__add__, P["cpu"], []))):
            a[index] = 1


def high_memory_intensity():
    """
    For a computationally intensive application,
    take the affinity that produces the faster runtime
    """
    socket_index = {}
    core_index = {}
    # Genereate our two affinities we want to test
    for socket_index in range(N):
        for core_index in range(M):
            cluster_affinity[socket_index][core_index] = \
                not not d["cpu"][socket_index][core_index]

            spread_affinity[core_index][socket_index] = \
                not not d["cpu"][socket_index][core_index]

    spread_time = time_process_with_affinity(spread_affinity)
    cluster_time = time_process_with_affinity(cluster_affinity)

    if (spread_time < cluster_time):
        return spread_affinity
    else:
        return cluster_affinity


def time_process_with_affinity(affinity):
    """
    Return the time an application takes to execute with a given core affinity
    affinity :: Array containing sockets as elements and core activation as elements
      ex : [[1, 1, 1], [1, 1, 0], [0, 0, 0]] = Three sockets, each with three cores, cores 0-4 are active
    """
    start_time = time.clock()
    affinity_command = ["taskset", affinity_to_string(affinity)]
    subprocess.call(application_command)
    total_time = time.clock() - start_time


# This is a dumb function, replace with some bit twiddling and convert the
# affinity array to a primitive int. Then use hex(affinity) to add to the command
def affinity_to_string(affinity):
    """
    Convert the affinity array to a string to be passed into taskset in time_process_with_affinity
    affinity :: Affinity array

    returns a string
      ex : [[1, 1, 1], [1, 1, 0], [0, 0, 0]] = "0x1F"
    """
    n_str = "0x"
    for n in affinity:
        n = map(lambda x: str(x), n)  # Convert everything to strings
        temp = ''.join(n)  # shove everything into one string
        n_str += hex(int(temp, 2))  # and convert it from base 2->10->16
    return n_str


# (W, SZ, Pb) -> ([a], [d])
# (program, problem size, power budget) -> ([a], [d])
def recommend_configuration(appCfg, rscCfg):
    """
    Suggest a configuration to run the application in.

    appCfg :: dict object from the apprunner section, specifies application information
    rscCfg :: dict object from the apprunner section, specifies resource information

    returns a pair (a, d) representing the core affinity and power distribution of the configuration
    """
    # Kick off the algorithm from step one from the paper
    Pb = rscCfg["power_allocation"]["cpu"]["total"] + \
         rscCfg["power_allocation"]["mem"]["total"]

    power_budget_is_sufficient(appCfg, Pb)
    # The fall-through of all the methods load up a and d
    return (a, d)
