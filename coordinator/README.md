
# To Run Coordinator

## Configure json inputs
There is an example pair of json input files provided in coordinator/config, use them as a template to fit your particular system. If you are unsure of the values to fill in, the following table provides some commands that might help you find them.

| Value     | Command  |
------------|----------
| hostname  | ```hostname```  |
| num_cores | ```lscpu ⎮ grep CPU```  |
| cpu sockets  | ```lscpu ⎮ grep Socket```  |
| cpu min/max freq | ```cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_{min,max}_freq```  |
| base_power_levels | Execute utils/read_base_levels.py |

## Execute the appRunner.py
The controller uses positional argements, for example:
~~~~
$ ./appRunner.py ../config/ep.json ../config/resource1.json False
~~~~
The final boolean provided tells the program to submit the job to the scheduler or not.

The appRunner will provide feedback as it executes and will create a <app>.job file even if asked not to submit it.
