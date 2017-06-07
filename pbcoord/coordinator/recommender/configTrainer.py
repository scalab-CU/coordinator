#!/usr/bin/env python
'''
Created on May 31, 2017

@author: tsranso
'''

from functools import reduce
import json
import datetime

# Number of Processors
N = 48 # $ nproc
# Number of cores per processor
M = 12 # $ grep cores /proc/cpuinfo
# Affinity map, true if that core is active
a = [[0 for m in range(M)] for n in range(N)]
# Power distribution vector
d = dict()
d["cpu"] = [[0 for m in range(M)] for k in range(N)]
d["mem"] = [0 for k in range(N)]

def power_budget_is_sufficient(Pb):
    
    if (Pb > P["cpu"][1] + P["mem"][1]):
        # Allocate max memory to all memory nodes
        single_memory_allocation = P["mem"][1] / N
        d["mem"] = [single_memory_allocation for k in range(N)]
        # Set thread concurrency and affinity from pivot execution configuration
        read_pivot_config()
        
    elif (Pb > P["cpu"][4] + P["mem"][2]):
        decide_memory_allocation(Pb)

    if (Pb < P["cpu"][4] + P["mem"][2]):
        # "power budget too low"
        return
    

def decide_memory_allocation(Pb):
    #if (Pb > P["cpu"][2] + P["mem"][1]):
        single_memory_allocation = P["mem"][1] / N
        d["mem"] = [single_memory_allocation for k in range(N)]
        decide_memory_allocation(Pb - P["mem"][1])

def update_indicies(socket_index, core_index):
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

def decide_core_allocation(application, Pb):
    if (application["scalability"] == "high"):
        
        socket_index = 0
        core_inedx = 0
        # Give power to as many cores as we can
        while Pb >= P["cpu"][4]:
            d["cpu"][socket_index][core_index] = P["cpu"][4]
            Pb -= P["cpu"][4]
            (socket_index, core_index) = update_indicies(socket_index, core_index)
        # and upgrade the power as the budget allows
        while (Pb >= P["cpu"][3]):
            d["cpu"][socket_index][core_inedx] = P["cpu"][3]
            (socket_index, core_inedx) = update_indicies(socket_index, core_inedx)
            # Because the memory is already set to L3, just take off the difference
            Pb -= (P["cpu"][3] - P["cpu"][4])
    # Purposefully not inverting this logic
    #   (loops inside ifs instead of ifs inside loops) for readability and to
    #   more closely follow the paper specification
    elif (application["scalability"] == "low"):
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
    else:
        return

def decide_core_affinity():

    if (application["memory_intensity"] == "high"):
        # Decide between high core clustering or more spread out
        a = high_memory_intensity()
    else:
        # Pack as many activated cores into the fewest sockets
        for index in range(sum(reduce(list.__add__, P["cpu"], []))):
            a[index] = 1

# For a computationally intenive application
def high_memory_intensity():
    socket_index = {};
    core_index = {};
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
    start_time = time.clock()
    affinity_command = ["taskset", affinity_to_string(affinity)]
    subprocess.call(application_command)
    total_time = time.clock() - start_time

# This is a dumb function, replace with some bit twiddling and convert the
# affinity array to a primitive int. Then use hex(affinity) to add to the command
def affinity_to_string(affinity):
    #flat_list = [y for x in affinity for y in x]
    n_str = "0x"
    for n in affinity:
        n = map(lambda x : str(x), n) # Convert everything to strings
        temp = ''.join(n) # shove everything into one string
        n_str += hex(int(temp, 2)) # and convert it from base 2->10->16
    return n_str

# (W, SZ, Pb) -> ([a], [d])
# (program, problem size, power budget) -> ([a], [d])
def recommend_configuration(appCfg, rscCfg):
    # Kick off the algorithm from step one from the paper
    Pb = rscCfg["power_allocation"]["cpu"]["total"] + \
         rscCfg["power_allocation"]["mem"]["total"];

    power_budget_is_sufficient(Pb)
    # The fall-through of all the methods load up a and d
    return (a, d)
