

# System requirements

* Python 2.7+
* C++ compiler (tested on g++ 4.8.5)
* MSR enabled platform
* root permissions (for setting power budget and reading power levels)

The testing system is an Intel Haswell based cluster, though we believe this system will work on most Intel based systems that support the rapl interface.


# To Run Coordinator
## Compile utilities
Run a quick make inside both the ```rapl-ctl``` and ```rapl-reader``` top directories to compile the power reader and the power bound setter.


## JSON configuration file inputs
There is an example pair of json input files provided in ```coordinator/config```, use them as a template to fit your particular system. 

### Description of configuration elements

#### problem.json
| Value | Description |
--------|-------------|
| app   |  Name of the problem application         |
| psize |  Problem size of applicaition (optional) |
| path  |  Full path to problem executable binary  |
| program model    |  Can only be 'omp' for now, used to configure job script  |
| scalability      |  Can be one of {'low', 'high'} |
| memory intensity |  Can be one of {'low', 'high'} |

#### resource.json
| Value | Description |
--------|-------------|
| wms | The job submission platform currently can only be 'torque' |
| rapl ctl location | full path to the ```rapl-ctl``` directory provided  |
| rapl reader location | full path to the ```rapl-reader``` directory provided  |
| power budget  | User defined power budget |
| num dram modules  | Number of modules on node |


## Executing the appRunner.py

After creating the json configuration files in the ```coordinator/config``` directory, you are ready to run the coordinator in ```coordinator/apprunner```. 

The controller uses positional argements, first is the problem description, followed by the resource descrription. The final boolean provided tells the program to submit the job to the scheduler or not. See the example run below and the template json files provided in pbcoord/coordinator/config for generic uses.

The appRunner will provide feedback as it executes and will create a <app>.job file even if asked not to submit it. 

### Example
A complete execution of the coordinator would look like this for a new problem
~~~~
$ ./appRunner.py ../config/ep.json ../config/resource.json False
Namespace(app_cfg='../config/ep.json', resource_cfg='../config/resource.json', submit_job='False')
Problem not known, recommending configuration
Determining base power levels
Determining critical power levels
Wrote power levels to knowledge base
Power budget is sufficient
Deciding Core Allocation
Deciding Core Affinity
Wrapper template filled
$ 
~~~~

A complete run as shown above will produce files in the kbase directory storing information collected during execution. When the appRunner detects that these files exist, it will default to use these values in order to save runtime.

Executing the appRunner with these files present looks like this
~~~~
$ ./appRunner.py ../config/ep.json ../config/resource.json False
Namespace(app_cfg='../config/ep.json', resource_cfg='../config/resource.json', submit_job='False')
Problem is known
Wrapper template filled
$
~~~~

The outputted job script will be in the ```coordinator``` directory named ```<problem_name>.job```.
