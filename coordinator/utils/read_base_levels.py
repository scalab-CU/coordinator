#!/usr/bin/env python

import time
import subprocess

def make_rapl_log(rapl_output_file):
    rapl_resolution = 0.1
    rapl_location = "/usr/local/bin"

    # gotta build that core string for rapl to read all our cores
    core_string = ""
    for i in range(24):
        core_string += str(i) + ","
    # but that last comma causes us some problems
    core_string = core_string[:-1]

    # we want the power of the entire socket, even if only running on one core
    rapl_command = ['sudo', rapl_location + '/rapl', '-s', str(rapl_resolution), '-c', core_string, '-f', rapl_output_file]
    rapl_pid = subprocess.Popen(rapl_command, stdout=subprocess.PIPE).pid
    time.sleep(5)
    subprocess.call(['sudo', 'kill', str(rapl_pid)])


def read_rapl(rapl_filename):

    cpu_powers = []
    mem_powers = []
        
    with open(rapl_filename, 'r') as rapl_log:
        next(rapl_log) # jump over the header line
        for line in rapl_log:
            line = ' '.join(line.split())
            line = line.split()
            for index in range(24):
                cpu_powers.append(float(line[4*index+2]))
                mem_powers.append(float(line[4*index+4]))

    subprocess.call(['sudo', 'rm', '-f', rapl_filename])
    
    # chop off the ends for rapl reading inconsistencies
    #print(str(sum(mem_powers[5:-5])/len(mem_powers[5:-5])))
    #print(str(sum(cpu_powers[5:-5])/len(cpu_powers[5:-5])))
    return (sum(mem_powers[5:-5])/len(mem_powers[5:-5]), sum(cpu_powers[5:-5])/len(cpu_powers[5:-5]))

make_rapl_log('/tmp/base_rapl.log')
(mem, cpu) = read_rapl('/tmp/base_rapl.log')

print "Base mem power:" + str(mem)
print "Base cpu power:" + str(cpu)

