#!/bin/sh

function usage() {

    echo "todo"
    exit 1
}

base_dir='/home/tsranso/pbcoord/pbcoord/coordinator/recommender'
bin_dir="$base_dir/bin"
kbase_dir="$base_dir/kbase"


benchmark='ep' # yay arbitrary choices!
size='C'
affinity='0-11,12-23'
freq=2300000
dry_run=false
# cpupower frequency-info | grep hardware-limits

while true; do
    case $1 in
	-a | --affinity)  affinity=$2;  shift; shift ;;
	-b | --benchmark) benchmark=$2; shift; shift ;;
	-s | --size)      size=$2;      shift; shift ;;
	-f | --low-frequency) freq=1200000; shift ;;
	-h | --help) usage ;;
	-d | --dry-run) dry_run=true; shift ;;
	*) break ;;
    esac
done

# echo "Benchmark: $benchmark"
# echo "Size: $size"
# echo "Affinity: $affinity"
# echo "Freq: $freq"

if [ "$dry_run" = true ]; then
    exit
fi

# Make a place for the data files if it's not already there
output_directory="$base_dir/perfDB"

if [ -e "/tmp/$benchmark.rapl.log" ]; then
    rm "/tmp/$benchmark.rapl.log"
fi

if [ ! -d "$output_directory" ]; then
    mkdir $output_directory
fi

# Start rapl
/usr/local/bin/rapl -s 0.1 -c 0,12 -f /tmp/$benchmark.rapl.log 2>&1 1>/dev/null &
# record the rapl process id
rapl_pid=$!
OMP_NUM_THREADS=24
GOMP_CPU_AFFINITY=$affinity
# start benchmark with task affinity
timeout 5 taskset -c $affinity $bin_dir/$benchmark.$size.x >> $output_directory/$benchmark.$size.data



kill ${rapl_pid}

