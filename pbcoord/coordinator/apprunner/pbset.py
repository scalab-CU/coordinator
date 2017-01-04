'''
Created on Jan 3, 2017

@author: fengx
'''
import argparse
import subprocess

def parsePowerArgment(arg):
    limits = {}
    if arg == None:
        return limits
    lst = arg.split(',')
    for e in lst:
        vs = e.split(":")
        if len(vs) >= 2:
            idx, power = int(vs[0]), float(vs[1])
            limits[idx] = power
    return limits

def showPowerLimits(limits, prefix):
    for k in sorted(limits.keys()):
        print("{0}{1} = {2}".format(prefix, k, limits[k]))

rapl_cmd = "/usr/local/bin/mu_power_gadget"
def setPowerLimits(pkg_power_limits, dram_power_limits):
    cmds = []
    
    for k in sorted(dram_power_limits.keys()):
        if k == 0:
            cmds.append([rapl_cmd, "-0", str(dram_power_limits[k])])
        elif k == 1:
            cmds.append([rapl_cmd, "-1", str(dram_power_limits[k])])
        else:
            print("incorrect DRAM package index {} (must be 0 or 1)".format(k))
    
    for k in sorted(pkg_power_limits.keys()):
        if k == 0:
            cmds.append([rapl_cmd, "-2", str(pkg_power_limits[k])])
        elif k == 1:
            cmds.append([rapl_cmd, "-3", str(pkg_power_limits[k])])
        else:
            print("incorrect CPU package index {} (must be 0 or 1)".format(k))
    
    for cmd in cmds:
        subprocess.call(cmds)
        
    
if __name__ == '__main__':
    p = argparse.ArgumentParser(description="set power bound on CPU packages and DRAM modules")
    p.add_argument('--pkg', help="set CPU package power limits, e.g.: --pkg 0:100,1:80")
    p.add_argument('--dram', help="set DRAM module power limits, e.g.: --dram 0:40,1:40")
    args = p.parse_args()
    print(args)
    
    pkg_power_limits = parsePowerArgment(args.pkg)
    dram_power_limits = parsePowerArgment(args.dram)
    showPowerLimits(pkg_power_limits, "PKG")
    showPowerLimits(dram_power_limits, "DRAM")
    
    setPowerLimits(pkg_power_limits, dram_power_limits)

