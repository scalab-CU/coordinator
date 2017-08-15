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
from math import floor
import json
import datetime
import subprocess

## Global variales yay python scripting
number_cores = int(subprocess.check_output(['nproc', '--all']))
number_sockets = int(subprocess.check_output('lscpu | grep Socket | cut -c20-', shell=True))

# Affinity map, 1 if that core is active, 0 otherwise
a = [[0 for m in range(number_cores)] for n in range(number_sockets)]
# Power distribution vector
d = dict()
d['cpu'] = [[0 for c in range(number_cores)] for s in range(number_sockets)]
d['mem'] =  [0 for s in range(number_sockets)]
# Critical power levels, filled in by script
P = dict()
P['cpu'] = [0, 0, 0, 0]
P['mem'] = [0, 0]

def print_info_about_globals():
    print ""

def median(L):
    if len(L) == 1:
        return floor(L[0])
    if len(L) == 2:
        return floor((L[0] + L[1]) / 2)
    return median(L[1:-1])


def power_budget_is_sufficient(appCfg, rscCfg, Pb):
    """
    Determine if there is enough power being supplied to continue with algorithm
    Pb :: Power Budget
    """
    # if (Pb > P['cpu'][0] + P['mem'][0]):
    #     # Allocate max memory to all memory nodes
    #     single_memory_allocation = P['mem'][0] / N
    #     d['mem'] = [single_memory_allocation for k in range(N)]
    #     # Set thread concurrency and affinity from pivot execution configuration
    #     print 'Power budget is sufficient, reading pivot file'
    #     #read_pivot_config()
    #     return True

    # the power budget is acceptable
    if (Pb > P['cpu'][3] + P['mem'][1]):
        Pb = decide_memory_allocation(rscCfg, Pb)
        # P['mem'][1] is assigned to memory in every situation, so just chop that right off
        print 'Power budget is sufficient'
        decide_core_allocation(appCfg, Pb)
        decide_core_affinity(appCfg)
        return True

    if (Pb < P['cpu'][3] + P['mem'][1]):
        # "power budget too low"
        return False


def decide_memory_allocation(rscCfg, Pb):
    """
    How is the power allocated to the memory?
    Pb :: Power Budget
    """
    # Paper never specifies to allocate anything other than L1 to the memory
    # because zero indexing... L1 -> P['mem'][0]
    #if (Pb > P['cpu'][2] + P['mem'][1]):
    modules = rscCfg['num_dram_modules']
    d['mem'] = [P['mem'][0] for k in range(modules)]
    return Pb - (modules * P['mem'][0])


def update_indicies(socket_index, core_index):
    """
    Utility function to correctly increment indicies for the decide_core_allocation method
    socket_index :: current socket index
    core_idex :: current core index
    """
    core_index += 1
    # Number of cores per processor
    if core_index == number_cores/number_sockets:
        core_index = 0
        socket_index += 1
    # Number of sockets
    if socket_index == number_sockets:
        core_index = 0
        socket_index = 0
    return (socket_index, core_index)


def decide_core_allocation(appCfg, Pb):
    """
    Determine the power allocated to the cores, store the data in the a array

    appCfg :: dict from appRunner, tells us the scalability here
    Pb :: Power Budget
    """
    socket_index = 0
    core_index = 0
    print "Deciding Core Allocation"
    if (appCfg['scalability'] == 'high'):

        while Pb >= (P['cpu'][2] - P['cpu'][3]):
            # Give power to as many cores as we can
            if d['cpu'][socket_index][core_index] == 0:
                # small logic problem here, sometimes overextended, maybe fix later
                Pb = Pb - P['cpu'][3]
                if Pb > 0:
                    d['cpu'][socket_index][core_index] = P['cpu'][3]
            # and upgrade as power is available
            else:
                d['cpu'][socket_index][core_index] == P['cpu'][2]
                Pb = Pb - (P['cpu'][2] - P['cpu'][3])    
            (socket_index, core_index) = update_indicies(socket_index, core_index)
            
    elif (appCfg['scalability'] == 'low'):
        # give max power to a low number of cores
        while Pb >= P['cpu'][3]:
            if Pb >= P['cpu'][2]:
                d['cpu'][socket_index][core_index] = P['cpu'][2]
                Pb = Pb - P['cpu'][2]
            else:
                d['cpu'][socket_index][core_index] = P['cpu'][3]
                Pb = Pb - P['cpu'][3]
            (socket_index, core_index) = update_indicies(socket_index, core_index)
    # at this point we know that the application scalability is moderate
    # TODO: this
    #else:
    #    return
    #print(d['cpu'])
    return d['cpu']

def decide_core_affinity(appCfg):
    """
    Edit the core affinity array (a) in accordance to the memory access intensity
    """
    global a
    print("Deciding Core Affinity")
    if (appCfg['memory_intensity'] == 'high'):
        # Decide between high core clustering or more spread out
        a = high_memory_intensity(appCfg)
    else:
        core_count = 0
        # Pack as many activated cores into the fewest sockets
        for socket_index in range(number_sockets):
            for core_index in range(number_cores / number_sockets):
                if (d['cpu'][socket_index][core_index] == 0):
                    a[socket_index][core_index] = 0
                else:
                    a[socket_index][core_index] = 1


def high_memory_intensity(appCfg):
    """
    For a computationally intensive application,
    take the affinity that produces the faster runtime
    """

    print("Application has high memory intensity")
    socket_index = {}
    core_index = {}
    # Genereate our two affinities we want to test
    for socket_index in range(number_sockets):
        for core_index in range(number_cores / number_sockets):
            cluster_affinity[socket_index][core_index] = \
                not not d['cpu'][socket_index][core_index]

            spread_affinity[core_index][socket_index] = \
                not not d['cpu'][socket_index][core_index]

    print("Measuring runtime with a spread affinity...")
    spread_time = time_process_with_affinity(appCfg, spread_affinity)
    print("\tDone")
    print("Measuring runtime with a clustered affinity...")
    cluster_time = time_process_with_affinity(appCfg, cluster_affinity)
    print("\tDone")

    if (spread_time < cluster_time):
        return spread_affinity
    else:
        return cluster_affinity


def time_process_with_affinity(appCfg, affinity):
    """
    Return the time an application takes to execute with a given core affinity
    affinity :: Array containing sockets as elements and core activation as elements
      ex : [[1, 1, 1], [1, 1, 0], [0, 0, 0]] = Three sockets, each with three cores, cores 0-4 are active
    """
    start_time = time.clock()
    affinity_command = ['taskset', '-c', affinity_to_string(affinity), appCfg['path']]
    subprcess.call(affinity_command)
    total_time = time.clock() - start_time


def affinity_to_string(affinity):
    """
    Convert the affinity array to a string to be passed into taskset in time_process_with_affinity
    affinity :: Affinity array

    returns a string
      ex : [[1, 1, 1], [1, 1, 0], [0, 0, 0]] = '1,2,3,4,5'
    """

    if affinity is None or affinity == []:
        return ""
    flat_affinity = [item for sublist in affinity for item in sublist]
    
    # pick out all the cores that are active and associate their indicies
    # and shove all their indices into 
    cores = zip(*filter(lambda x : x[1] == 1, enumerate(flat_affinity)))[0]

    return ','.join(str(core) for core in cores)


def make_rapl_log(appCfg, rscCfg, frequency, cores):
    """
    appCfg - used for path, app, [psize]
    rscCfg - used for num_cores to get all rapl core readings
    frequency - used to test power with frequency
    cores::string - "one" or "all"
    """
    rapl_resolution = 0.1
    rapl_location = rscCfg['rapl_reader_location']
    # if there is a problem size provided, use it in the rapl log name
    if 'psize' in appCfg:
        rapl_output_file = "/tmp/{}.rapl.log".format(appCfg['app'] + '.' + appCfg['psize'])
    else:
        rapl_output_file = "/tmp/{}.rapl.log".format(appCfg['app'] + '.' + appCfg['psize'])

    #print "Frequency: {}".format(frequency)
    #print "Cores: {}".format(cores)
        
    # we want the power of the entire socket, even if only running on one core
    rapl_command = ['sudo', rapl_location + '/rapl', '-s', str(rapl_resolution), '-c', '0,12', '-f', rapl_output_file]

    # this is what limits the benchmark to the determined cores
    benchmark_command = []
    if cores == "one":
        benchmark_command = ['timeout', '8', 'taskset', '-c', '0', appCfg['path']]
    else:
        benchmark_command = ['timeout', '8',  appCfg['path']]

    #print("Adjusting frequencies")
    # TODO: this is less than good, prompt the user and do an echo "$pass" | sudo -S "stuff"
    frequency_command = ['sudo', 'cpupower', 'frequency-set', '-f', str(frequency)]
    subprocess.call(frequency_command, stdout=subprocess.PIPE)
    
    rapl_pid = subprocess.Popen(rapl_command, stdout=subprocess.PIPE).pid

    # using call here instead of popen to block
    subprocess.call(benchmark_command, stdout=subprocess.PIPE)

    subprocess.call(['sudo', 'kill', str(rapl_pid)])
    #print("Killed rapl process")
    #print("Restoring frequencies")
    # put the cpus back to max frequency so we don't mess up the system for other users
    high_frequency = subprocess.check_output(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq'])
    frequency_command = ['sudo', 'cpupower', 'frequency-set', '-f', high_frequency]
    subprocess.call(frequency_command, stdout=subprocess.PIPE)
    #print("Rapl log generated")


def determine_critical_power_levels(appCfg, rscCfg):
    """
    Run the measure_power.sh script to output the rapl data. The rapl data is then 
    read in and the maximum value read is stored as the critical power level
    """
    print("Determining critical power levels")

    high_frequency = int(subprocess.check_output(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq']))
    low_frequency  = int(subprocess.check_output(['cat', '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq']))
    
    # run with one core at minimum freq
    make_rapl_log(appCfg, rscCfg, low_frequency, 'one')
    power_levels = read_rapl(appCfg)
    P['mem'][1] = power_levels[0]
    P['cpu'][3] = power_levels[1]
    
    # run with one core at maximum freq
    make_rapl_log(appCfg, rscCfg, high_frequency, 'one')
    P['cpu'][2] = read_rapl(appCfg)[1]

    # run with all cores at maximum freq    
    make_rapl_log(appCfg, rscCfg, high_frequency, 'all')
    power_levels = read_rapl(appCfg)
    P['mem'][0] = power_levels[0]
    P['cpu'][0] = power_levels[1]
    
    # run with all cores at minimum freq
    make_rapl_log(appCfg, rscCfg, low_frequency, 'all')
    P['cpu'][1] = read_rapl(appCfg)[1]

    #print('\n\tDone: ' + str(P))
    # for index, e in enumerate(P['mem']):
    #     print "{} - {}".format(index, P['mem'][index])
    # for index, e in enumerate(P['cpu']):
    #     print "{} - {}".format(index, P['cpu'][index])
    return P


def read_rapl(appCfg):

    cpu_powers = []
    mem_powers = []
    if 'psize' in appCfg:
        rapl_filename = '/tmp/{}.{}.rapl.log'.format(appCfg['app'], appCfg['psize'])
    else:
        rapl_filename = '/tmp/{}.rapl.log'.format(appCfg['app'])
        
    with open(rapl_filename, 'r') as rapl_log:
        next(rapl_log) # jump over the header line
        for line in rapl_log:
            line = ' '.join(line.split())
            line = line.split()
            cpu_powers.append(float(line[2]))
            cpu_powers.append(float(line[6]))
            mem_powers.append(float(line[4]))
            mem_powers.append(float(line[8]))

    #print mem_powers
    #print cpu_powers
    #subprocess.call(['cp', rapl_filename, '../kbase/'])
    subprocess.call(['sudo', 'rm', '-f', rapl_filename])
    
    # chop off the ends for rapl reading inconsistencies
    return (median(mem_powers[5:-5]), median(cpu_powers[5:-5]))


# (W, SZ, Pb) -> ([a], [d])
# (program, problem size, power budget) -> ([a], [d])
def recommend_configuration(appCfg, rscCfg, powerCfg):
    """
    Suggest a configuration to run the application in.

    appCfg :: dict object from the apprunner section, specifies application information
    rscCfg :: dict object from the apprunner section, specifies resource information

    returns a pair (a, d) representing the core affinity and power distribution of the configuration
    """

    # Fill in the P array for power levels
    if not 'critical_power_levels' in powerCfg:
        determine_critical_power_levels(appCfg, rscCfg)
    else:
        #print "Critical power levels predetermined"
        global P
        P = powerCfg['critical_power_levels']
        
    # Kick off the algorithm from step one from the paper
    Pb = rscCfg['power_budget']

    power_budget_is_sufficient(appCfg, rscCfg, Pb)
    # The fall-through of all the methods load up a and d
    return (a, d)
