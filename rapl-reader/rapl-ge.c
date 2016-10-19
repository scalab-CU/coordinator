/* Read the RAPL registers on a sandybridge-ep machine                */
/* Code based on Intel RAPL driver by Zhang Rui <rui.zhang@intel.com> */
/*                                                                    */
/* The /dev/cpu/??/msr driver must be enabled and permissions set     */
/* to allow read access for this to work.                             */
/*                                                                    */
/* Compile with:   gcc -O2 -Wall -o rapl_msr rapl_msr.c -lm           */
/*                                                                    */
/* Vince Weaver -- vweaver1@eecs.utk.edu -- 16 March 2012             */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <inttypes.h>
#include <unistd.h>
#include <math.h>
#include <sys/time.h>
#include <setjmp.h>
#include <signal.h>

#define DEFAULT_RAPL_LOG	"rapl.log"

#define MSR_RAPL_POWER_UNIT		0x606

/*
 * Platform specific RAPL Domains.
 * Note that PP1 RAPL Domain is supported on 062A only
 * And DRAM RAPL Domain is supported on 062D only
 */
/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT	0x610
#define MSR_PKG_ENERGY_STATUS		0x611
#define MSR_PKG_PERF_STATUS		0x613
#define MSR_PKG_POWER_INFO		0x614

/* PP0 RAPL Domain */
#define MSR_PP0_POWER_LIMIT		0x638
#define MSR_PP0_ENERGY_STATUS	0x639
#define MSR_PP0_POLICY			0x63A
#define MSR_PP0_PERF_STATUS		0x63B

/* PP1 RAPL Domain, may reflect to uncore devices */
#define MSR_PP1_POWER_LIMIT		0x640
#define MSR_PP1_ENERGY_STATUS	0x641
#define MSR_PP1_POLICY			0x642

/* DRAM RAPL Domain */
#define MSR_DRAM_POWER_LIMIT	0x618
#define MSR_DRAM_ENERGY_STATUS	0x619
#define MSR_DRAM_PERF_STATUS	0x61B
#define MSR_DRAM_POWER_INFO		0x61C

/* RAPL UNIT BITMASK */
#define POWER_UNIT_OFFSET	0
#define POWER_UNIT_MASK		0x0F

#define ENERGY_UNIT_OFFSET	0x08
#define ENERGY_UNIT_MASK	0x1F00

#define TIME_UNIT_OFFSET	0x10
#define TIME_UNIT_MASK		0xF000

int open_msr(int core) {

	char msr_filename[BUFSIZ];
	int fd;

	sprintf(msr_filename, "/dev/cpu/%d/msr", core);
	fd = open(msr_filename, O_RDONLY);
	if (fd < 0) {
		if (errno == ENXIO) {
			fprintf(stderr, "rdmsr: No CPU %d\n", core);
			exit(2);
		} else if (errno == EIO) {
			fprintf(stderr, "rdmsr: CPU %d doesn't support MSRs\n", core);
			exit(3);
		} else {
			perror("rdmsr:open");
			fprintf(stderr, "Trying to open %s\n", msr_filename);
			exit(127);
		}
	}

	return fd;
}

long long read_msr(int fd, int which) {

	uint64_t data;

	if (pread(fd, &data, sizeof data, which) != sizeof data) {
		perror("rdmsr:pread");
		exit(127);
	}

	return (long long) data;
}

//show_usage: print usage of this program
void show_usage(char *prog) {
	fprintf(stderr, "%s -s sample_interval -f log_file\n", prog);
	fprintf(stderr, "%s -h\n", prog);
	exit(0);
}

static jmp_buf env;

//sig_int: a signal handler for signal SIG_INT
static void sig_int(int signo) {
	longjmp(env, 1);
}

int main(int argc, char **argv) {
	int fd[2];
	int core[2] = { 0, 31 };
	char * logfile;
	FILE *logfd;
	int interval = 1;
	int i;
	long long result;
	double power_units, energy_units, time_units;
	double package_before[2], package_after[2];
	double pp0_before[2], pp0_after[2];
	double pp1_before[2], pp1_after[2];
	double dram_before[2], dram_after[2];
	double package_power[2], pp0_power[2], pp1_power[2], dram_power[2];
	double thermal_spec_power, minimum_power, maximum_power, time_window;
	struct timeval start, end;

	printf("\n");

	int option;
	int opterr = 0;

	logfile = DEFAULT_RAPL_LOG;
	printf("logfile name: %s\n", logfile);

	while ( (option = getopt(argc, argv, "hf:s:")) != -1) {
		switch (option) {
		case 'f':
			logfile = optarg;
			break;
		case 's':
			interval = atoi(optarg);
			break;
		case 'h':
			show_usage(argv[0]);
			break;
		default:
			show_usage(argv[0]);
			break;
		}
	}

	fprintf(stdout, "settings: log_file=%s\tinterval=%d\n", logfile, interval);

	fd[0] = open_msr(core[0]);
	fd[1] = open_msr(core[1]);

	if ((logfd = fopen(logfile, "w+")) == NULL) {
		fprintf(stderr, "\nOpen log file %s failed at %s:%d\n", logfile, __FILE__, __LINE__);
		exit(-1);
	}

	if (setjmp(env) == 0) {

		if (signal(SIGINT, sig_int) != 0) {
			fprintf(stderr, "calling signal failed at %s:%d\n", __FILE__,
					__LINE__);
			exit(-1);
		}
		/* Calculate the units used */
		result = read_msr(fd[0], MSR_RAPL_POWER_UNIT);

		power_units = pow(0.5, (double) (result & 0xf));
		energy_units = pow(0.5, (double) ((result >> 8) & 0x1f));
		time_units = pow(0.5, (double) ((result >> 16) & 0xf));

		printf("Power units = %.3fW\n", power_units);
		printf("Energy units = %.8fJ\n", energy_units);
		printf("Time units = %.8fs\n", time_units);
		printf("\n");

		/* Show package power info */
		result = read_msr(fd[0], MSR_PKG_POWER_INFO);
		thermal_spec_power = power_units * (double) (result & 0x7fff);
		printf("Package thermal spec: %.3fW\n", thermal_spec_power);
		minimum_power = power_units * (double) ((result >> 16) & 0x7fff);
		printf("Package minimum power: %.3fW\n", minimum_power);
		maximum_power = power_units * (double) ((result >> 32) & 0x7fff);
		printf("Package maximum power: %.3fW\n", maximum_power);
		time_window = time_units * (double) ((result >> 48) & 0x7fff);
		printf("Package maximum time window: %.3fs\n", time_window);
		result = read_msr(fd[0], MSR_RAPL_POWER_UNIT);

		printf("\n");

		gettimeofday(&start, NULL);
		for (i = 0; i < 2; i++) {

			result = read_msr(fd[i], MSR_PKG_ENERGY_STATUS);
			package_before[i] = (double) result * energy_units;
			//printf("Package energy before: %.6fJ\n", package_before[i]);

			result = read_msr(fd[i], MSR_PP0_ENERGY_STATUS);
			pp0_before[i] = (double) result * energy_units;
			//printf("PowerPlane0 (core) for core %d energy before: %.6fJ\n", core,	pp0_before);

			/* not available on SandyBridge-EP */
#if 0
			result=read_msr(fd[i],MSR_PP1_ENERGY_STATUS);
			pp1_before[i] = (double)result*energy_units;
			//printf("PP1 (on-core GPU if avail) before: %.6fJ\n",pp1_before);
#endif

			result = read_msr(fd[i], MSR_DRAM_ENERGY_STATUS);
			dram_before[i] = (double) result * energy_units;
			//printf("DRAM energy before: %.6fJ\n", dram_before);
		}

		printf("\nSleeping %d second\n\n", interval);

		while (1) {

			sleep(interval);

			gettimeofday(&end, NULL);
			for (i = 0; i < 2; i++) {
				result = read_msr(fd[i], MSR_PKG_ENERGY_STATUS);
				package_after[i] = (double) result * energy_units;
				package_power[i] = (package_after[i] - package_before[i])/interval;
				package_before[i] = package_after[i];

				result = read_msr(fd[i], MSR_PP0_ENERGY_STATUS);
				pp0_after[i] = (double) result * energy_units;
				pp0_power[i] = (pp0_after[i] - pp0_before[i])/interval;
				pp0_before[i] = pp0_after[i];

				/* not available on SandyBridge-EP */
				/*#if 0
				 result=read_msr(fd[i],MSR_PP1_ENERGY_STATUS);
				 pp1_after[i] = (double)result*energy_units;
				 pp1_power[i] = pp1_after[i] - pp1_before[i];
				 pp1_before[i] = pp1_after[i];

				 #endif

				 */result = read_msr(fd[i], MSR_DRAM_ENERGY_STATUS);
				dram_after[i] = (double) result * energy_units;
				dram_power[i] = (dram_after[i] - dram_before[i])/interval;
				dram_before[i] = dram_after[i];

				printf("printing\n");
				fprintf(logfd, "%ld.%06ld\t", end.tv_sec, end.tv_usec);
				fprintf(stdout, "%ld.%06ld\t", end.tv_sec, end.tv_usec);
				for (i = 0; i < 2; i++) {
					fprintf(stdout, "\t%.6fJ\t%.6fJ\t%.6fJ", package_power[i],
							pp0_power[i], dram_power[i]);
					fprintf(logfd, "\t%.6fJ\t%.6fJ\t%.6fJ", package_power[i],
							pp0_power[i], dram_power[i]);
				}
				fprintf(stdout, "\n");
				fprintf(logfd, "\n");

			}
		}
	} else {
		printf("\n");
		printf("Note: the energy measurements can overflow in 60s or so\n");
		printf("      so try to sample the counters more often than that.\n\n");
		close(fd[0]);
		close(fd[1]);
		fclose(logfd);
	}

	return 0;
}
