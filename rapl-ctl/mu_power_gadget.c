/*
 Copyright (c) 2012, Intel Corporation

 Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Intel Corporation nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/* Written by Martin Dimitrov, Carl Strickland */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <sys/time.h>
#include <time.h>
#include <signal.h>
#include <stdbool.h>

#include "rapl.h"

char *progname;
const char *version = "2.2";
uint64_t num_node = 0;
uint64_t delay_us = 1000000;
double duration = 3600.0;
double delay_unit = 1000000.0;

uint64_t pkg_power_limit = 0;
/* Edited by Yang */
uint64_t dram_power_limit = 0;
//double dram_power_limit = 0;
uint64_t pp0_power_limit = 0;
bool power_monitor_mode = false;
bool pkg_power_limit_mode = false;
bool pkg0_power_limit_mode = false;
bool pkg1_power_limit_mode = false;
bool dram_power_limit_mode = false;
//Added by Yang 3/22/2016
bool dram0_power_limit_mode = false;
bool dram1_power_limit_mode = false;
bool pp0_power_limit_mode = false;
bool print_power_limit = false;
bool print_units = false;
bool print_min_max_parameters = false;
bool print_summary = false;
FILE* power_log_file_handle;

extern double RAPL_TIME_UNIT;
extern double RAPL_ENERGY_UNIT;
extern double RAPL_POWER_UNIT;

double get_rapl_energy_info(uint64_t power_domain, uint64_t node) {
	int err;
	double total_energy_consumed;

	switch (power_domain) {
	case PKG:
		err = get_pkg_total_energy_consumed(node, &total_energy_consumed);
		break;
	case PP0:
		err = get_pp0_total_energy_consumed(node, &total_energy_consumed);
		break;
	case PP1:
		err = get_pp1_total_energy_consumed(node, &total_energy_consumed);
		break;
	case DRAM:
		err = get_dram_total_energy_consumed(node, &total_energy_consumed);
		break;
	default:
		err = MY_ERROR;
		break;
	}

	return total_energy_consumed;
}

void convert_time_to_string(struct timeval tv, char* time_buf) {
	time_t sec;
	int msec;
	struct tm *timeinfo;
	char tmp_buf[9];

	sec = tv.tv_sec;
	timeinfo = localtime(&sec);
	msec = tv.tv_usec / 1000;

	strftime(tmp_buf, 9, "%H:%M:%S", timeinfo);
	sprintf(time_buf, "%s:%d", tmp_buf, msec);
}

double convert_time_to_sec(struct timeval tv) {
	double elapsed_time = (double) (tv.tv_sec)
			+ ((double) (tv.tv_usec) / 1000000);
	return elapsed_time;
}

void do_print_pkg_power_limit_control(pkg_rapl_power_limit_control_t pkg_obj) {
	fprintf(power_log_file_handle, "pkg_power_limit_watts_1 = %f\n",
			pkg_obj.power_limit_watts_1);
	fprintf(power_log_file_handle, "pkg_power_limit_watts_2 = %f\n",
			pkg_obj.power_limit_watts_2);
	fprintf(power_log_file_handle, "pkg_clamp_enabled_1 = %d\n", pkg_obj.clamp_enabled_1);
	fprintf(power_log_file_handle, "pkg_clamp_enabled_2 = %d\n", pkg_obj.clamp_enabled_2);
	fprintf(power_log_file_handle, "pkg_limit_enabled_1 = %d\n", pkg_obj.limit_enabled_1);
	fprintf(power_log_file_handle, "pkg_limit_enabled_2 = %d\n", pkg_obj.limit_enabled_2);
	fprintf(power_log_file_handle, "pkg_limit_time_windows_1 = %f\n",
			pkg_obj.limit_time_window_seconds_1);
	fprintf(power_log_file_handle, "pkg_limit_time_windows_2 = %f\n",
			pkg_obj.limit_time_window_seconds_2);
	fprintf(power_log_file_handle, "pkg_lock_enabled = %d\n", pkg_obj.lock_enabled);
}

void do_print_pp0_power_limit_control(pp0_rapl_power_limit_control_t pp0_obj) {
	fprintf(power_log_file_handle, "pp0_power_limit_watts = %f\n", pp0_obj.power_limit_watts);
	fprintf(power_log_file_handle, "pp0_clamp_enabled = %d\n", pp0_obj.clamp_enabled);
	fprintf(power_log_file_handle, "pp0_limit_enabled = %d\n", pp0_obj.limit_enabled);
	fprintf(power_log_file_handle, "pp0_limit_time_windows = %f\n",
			pp0_obj.limit_time_window_seconds);
	fprintf(power_log_file_handle, "pp0_lock_enabled = %d\n", pp0_obj.lock_enabled);
}

void do_print_dram_power_limit_control(dram_rapl_power_limit_control_t dram_obj) {
	/*Edit by Yang for testing*/
	//printf("%f\n",dram_obj.power_limit_watts);
	fprintf(power_log_file_handle, "dram_power_limit_watts = %f\n",
			dram_obj.power_limit_watts);
	fprintf(power_log_file_handle, "dram_clamp_enabled = %d\n", dram_obj.clamp_enabled);
	fprintf(power_log_file_handle, "dram_limit_enabled = %d\n", dram_obj.limit_enabled);
	fprintf(power_log_file_handle, "dram_limit_time_windows = %f\n",
			dram_obj.limit_time_window_seconds);
	fprintf(power_log_file_handle, "dram_lock_enabled = %d\n", dram_obj.lock_enabled);
}

void do_print_power_limits() {
	int i, ret = 0;

	/* Get the power limit per node */
	for (i = 0; i < num_node; i++) {

		pkg_rapl_power_limit_control_t pkg_obj;
		pp0_rapl_power_limit_control_t pp0_obj;
		dram_rapl_power_limit_control_t dram_obj;

		ret = get_pkg_rapl_power_limit_control(i, &pkg_obj);
		if (ret != 0) {
			fprintf(stderr,
					"Failed to get the package power limit for node %d\n", i);
			perror(0);
		}

		ret = get_pp0_rapl_power_limit_control(i, &pp0_obj);
		if (ret != 0) {
			fprintf(stderr, "Failed to get the pp0 power limit for node %d\n",
					i);
			perror(0);
		}

		ret = get_dram_rapl_power_limit_control(i, &dram_obj);
		if (ret != 0) {
			fprintf(stderr, "Failed to get the dram power limit for node %d\n",
					i);
			perror(0);
		}

		// print the limits
		fprintf(power_log_file_handle, "\n\n\n\n", i);
		fprintf(power_log_file_handle, "Limits for node %d are: \n", i);
		fprintf(power_log_file_handle, "========================\n", i);
		do_print_pkg_power_limit_control(pkg_obj);
		fprintf(power_log_file_handle, "\n");
		do_print_pp0_power_limit_control(pp0_obj);
		fprintf(power_log_file_handle, "\n");
		do_print_dram_power_limit_control(dram_obj);
		fprintf(power_log_file_handle, "========================\n", i);
	}
}

void do_print_units() {
	fprintf(power_log_file_handle, "\n\n\n\n");
	fprintf(power_log_file_handle, "Power units are: \n");
	fprintf(power_log_file_handle, "RAPL_TIME_UNIT is: %f\n", RAPL_TIME_UNIT);
	fprintf(power_log_file_handle, "RAPL_ENERGY_UNIT is: %f\n", RAPL_ENERGY_UNIT);
	fprintf(power_log_file_handle, "RAPL_POWER_UNIT is: %f\n", RAPL_POWER_UNIT);
}

void do_print_min_max_parameters() {
	int i, ret = 0;

	/* Get the power min max parameters per node */
	for (i = 0; i < num_node; i++) {

		pkg_rapl_parameters_t pkg_param_obj;
		dram_rapl_parameters_t dram_param_obj;

		ret = get_pkg_rapl_parameters(i, &pkg_param_obj);
		if (ret != 0) {
			fprintf(stderr,
					"Failed to get the package parameters for node %d\n", i);
			perror(0);
		}

		ret = get_dram_rapl_parameters(i, &dram_param_obj);
		if (ret != 0) {
			fprintf(stderr, "Failed to get the dram parameters for node %d\n",
					i);
			perror(0);
		}

		// print the limits
		fprintf(power_log_file_handle, "\n\n\n\n", i);
		fprintf(power_log_file_handle, "Min Max limits for node %d are: \n", i);
		fprintf(power_log_file_handle, "========================\n", i);
		fprintf(power_log_file_handle, "pkg_thermal_spec_power_watts = %f\n",
				pkg_param_obj.thermal_spec_power_watts);
		fprintf(power_log_file_handle, "pkg_minimum_power_watts = %f\n",
				pkg_param_obj.minimum_power_watts);
		fprintf(power_log_file_handle, "pkg_maximum_power_watts = %f\n",
				pkg_param_obj.maximum_power_watts);
		fprintf(power_log_file_handle, "pkg_maximum_limit_time_window_seconds = %f\n",
				pkg_param_obj.maximum_limit_time_window_seconds);
		fprintf(power_log_file_handle, "\n");
		fprintf(power_log_file_handle, "dram_thermal_spec_power_watts = %f\n",
				dram_param_obj.thermal_spec_power_watts);
		fprintf(power_log_file_handle, "dram_minimum_power_watts = %f\n",
				dram_param_obj.minimum_power_watts);
		fprintf(power_log_file_handle, "dram_maximum_power_watts = %f\n",
				dram_param_obj.maximum_power_watts);
		fprintf(power_log_file_handle, "dram_maximum_limit_time_window_seconds = %f\n",
				dram_param_obj.maximum_limit_time_window_seconds);
		fprintf(power_log_file_handle, "========================\n", i);
	}
}

void do_print_energy_info() {
	int i = 0;
	int domain = 0;
	uint64_t node = 0;
	double new_sample;
	double delta;
	double power;

	double prev_sample[num_node][RAPL_NR_DOMAIN];
	double power_watt[num_node][RAPL_NR_DOMAIN];
	double cum_energy_J[num_node][RAPL_NR_DOMAIN];
	double cum_energy_mWh[num_node][RAPL_NR_DOMAIN];

	char time_buffer[32];
	struct timeval tv;
	int msec;
	uint64_t tsc;
	uint64_t freq;
	double start, end, interval_start;
	double total_elapsed_time;
	double interval_elapsed_time;
	time_t unix_time;

	/* don't buffer if piped */
	setbuf(stdout, NULL);

	/* Print header */
	fprintf(power_log_file_handle, "System Time,Unix Time,RDTSC,Elapsed Time (sec),");
	for (i = node; i < num_node; i++) {
		fprintf(power_log_file_handle, "IA Frequency_%d (MHz),", i);
		if (is_supported_domain(RAPL_PKG))
			fprintf(power_log_file_handle,
					"Processor Power_%d (Watt),Cumulative Processor Energy_%d (Joules),Cumulative Processor Energy_%d (mWh),",
					i, i, i);
		if (is_supported_domain(RAPL_PP0))
			fprintf(power_log_file_handle,
					"IA Power_%d (Watt),Cumulative IA Energy_%d (Joules),Cumulative IA Energy_%d (mWh),",
					i, i, i);
		if (is_supported_domain(RAPL_PP1))
			fprintf(power_log_file_handle,
					"GT Power_%d (Watt),Cumulative GT Energy_%d (Joules),Cumulative GT Energy_%d (mWh),",
					i, i, i);
		if (is_supported_domain(RAPL_DRAM))
			fprintf(power_log_file_handle,
					"DRAM Power_%d (Watt),Cumulative DRAM Energy_%d (Joules),Cumulative DRAM Energy_%d (mWh),",
					i, i, i);
	}
	fprintf(power_log_file_handle, "\n");

	/* Read initial values */
	for (i = node; i < num_node; i++) {
		for (domain = 0; domain < RAPL_NR_DOMAIN; ++domain) {
			if (is_supported_domain(domain)) {
				prev_sample[i][domain] = get_rapl_energy_info(domain, i);
			}
		}
	}

	gettimeofday(&tv, NULL);
	start = convert_time_to_sec(tv);
	end = start;

	/* Begin sampling */
	while (1) {

		usleep(delay_us);

		gettimeofday(&tv, NULL);
		interval_start = convert_time_to_sec(tv);
		interval_elapsed_time = interval_start - end;

		for (i = node; i < num_node; i++) {
			for (domain = 0; domain < RAPL_NR_DOMAIN; ++domain) {
				if (is_supported_domain(domain)) {
					new_sample = get_rapl_energy_info(domain, i);
					delta = new_sample - prev_sample[i][domain];

					/* Handle wraparound */
					if (delta < 0) {
						delta += MAX_ENERGY_STATUS_JOULES;
					}

					prev_sample[i][domain] = new_sample;

					// Use the computed elapsed time between samples (and not
					// just the sleep delay, in order to more accourately account for
					// the delay between samples
					power_watt[i][domain] = delta / interval_elapsed_time;
					cum_energy_J[i][domain] += delta;
					cum_energy_mWh[i][domain] = cum_energy_J[i][domain] / 3.6; // mWh
				}
			}
		}

		gettimeofday(&tv, NULL);
		end = convert_time_to_sec(tv);
		total_elapsed_time = end - start;
		convert_time_to_string(tv, time_buffer);
		unix_time = tv.tv_sec;

		read_tsc(&tsc);
		fprintf(power_log_file_handle, "%s,%ld,%llu,%.4lf,", time_buffer, (long) unix_time,
				tsc, total_elapsed_time);
		for (i = node; i < num_node; i++) {
			get_pp0_freq_mhz(i, &freq);
			fprintf(power_log_file_handle, "%u,", freq);
			for (domain = 0; domain < RAPL_NR_DOMAIN; ++domain) {
				if (is_supported_domain(domain)) {
					fprintf(power_log_file_handle, "%.4lf,%.4lf,%.4lf,", power_watt[i][domain],
							cum_energy_J[i][domain], cum_energy_mWh[i][domain]);
				}
			}
		}
		fprintf(power_log_file_handle, "\n");

		// check to see if we are done
		if (total_elapsed_time >= duration)
			break;
	}

	end = clock();

	/* Print summary */
	if (print_summary) {
		fprintf(power_log_file_handle, "\nTotal Elapsed Time(sec)=%.4lf\n\n",
				total_elapsed_time);
		for (i = node; i < num_node; i++) {
			if (is_supported_domain(RAPL_PKG)) {
				fprintf(power_log_file_handle, "Total Processor Energy_%d(Joules)=%.4lf\n", i,
						cum_energy_J[i][RAPL_PKG]);
				fprintf(power_log_file_handle, "Total Processor Energy_%d(mWh)=%.4lf\n", i,
						cum_energy_mWh[i][RAPL_PKG]);
				fprintf(power_log_file_handle, "Average Processor Power_%d(Watt)=%.4lf\n\n", i,
						cum_energy_J[i][RAPL_PKG] / total_elapsed_time);
			}
			if (is_supported_domain(RAPL_PP0)) {
				fprintf(power_log_file_handle, "Total IA Energy_%d(Joules)=%.4lf\n", i,
						cum_energy_J[i][RAPL_PP0]);
				fprintf(power_log_file_handle, "Total IA Energy_%d(mWh)=%.4lf\n", i,
						cum_energy_mWh[i][RAPL_PP0]);
				fprintf(power_log_file_handle, "Average IA Power_%d(Watt)=%.4lf\n\n", i,
						cum_energy_J[i][RAPL_PP0] / total_elapsed_time);
			}
			if (is_supported_domain(RAPL_PP1)) {
				fprintf(power_log_file_handle, "Total GT Energy_%d(Joules)=%.4lf\n", i,
						cum_energy_J[i][RAPL_PP1]);
				fprintf(power_log_file_handle, "Total GT Energy_%d(mWh)=%.4lf\n", i,
						cum_energy_mWh[i][RAPL_PP1]);
				fprintf(power_log_file_handle, "Average GT Power_%d(Watt)=%.4lf\n\n", i,
						cum_energy_J[i][RAPL_PP1] / total_elapsed_time);
			}
			if (is_supported_domain(RAPL_DRAM)) {
				fprintf(power_log_file_handle, "Total DRAM Energy_%d(Joules)=%.4lf\n", i,
						cum_energy_J[i][RAPL_DRAM]);
				fprintf(power_log_file_handle, "Total DRAM Energy_%d(mWh)=%.4lf\n", i,
						cum_energy_mWh[i][RAPL_DRAM]);
				fprintf(power_log_file_handle, "Average DRAM Power_%d(Watt)=%.4lf\n\n", i,
						cum_energy_J[i][RAPL_DRAM] / total_elapsed_time);
			}
		}
		read_tsc(&tsc);
		fprintf(power_log_file_handle, "TSC=%llu\n", tsc);
	}
}

void do_limit_pkg_power() {
	int i = 0;
	int domain = 0;
	uint64_t node = 0;
	int ret = -1;

	pkg_rapl_power_limit_control_t pkg_obj;
    
    if (pkg_power_limit == -1) { // disable power limit
        pkg_obj.power_limit_watts_1 = 0; // dummy
        pkg_obj.limit_enabled_1 = 0;
        pkg_obj.clamp_enabled_1 = 0;
        pkg_obj.power_limit_watts_2 = 0; // dummy
        pkg_obj.limit_enabled_2 = 0;
        pkg_obj.clamp_enabled_2 = 0;
        pkg_obj.lock_enabled = 0;
    } else {
        pkg_obj.power_limit_watts_1 = pkg_power_limit;
        pkg_obj.limit_enabled_1 = 1;
        pkg_obj.clamp_enabled_1 = 1;
        pkg_obj.limit_time_window_seconds_1 = 24*60*60; // for the day - hardcoded
        pkg_obj.power_limit_watts_2 = pkg_power_limit; // Keeping high limit for shorter duration
        pkg_obj.limit_enabled_2 = 1;
        pkg_obj.clamp_enabled_2 = 1;
        pkg_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
    }

	/* Set the package power limit */
	for (i = node; i < num_node; i++) {
		ret = set_pkg_rapl_power_limit_control(i, &pkg_obj);
		if (ret != 0) {
			fprintf(stderr,
					"Failed to set the package power limit for node %d\n", i);
		}
	}
}

void do_limit_pkg0_power() {
	int domain = 0;
	int ret = -1;

	pkg_rapl_power_limit_control_t pkg_obj;
    
    	if (pkg_power_limit == -1) { // disable power limit
        	pkg_obj.power_limit_watts_1 = 0; // dummy
	        pkg_obj.limit_enabled_1 = 0;
        	pkg_obj.clamp_enabled_1 = 0;
        	pkg_obj.power_limit_watts_2 = 0; // dummy
	        pkg_obj.limit_enabled_2 = 0;
	        pkg_obj.clamp_enabled_2 = 0;
	        pkg_obj.lock_enabled = 0;
    	} else {
	        pkg_obj.power_limit_watts_1 = pkg_power_limit;
	        pkg_obj.limit_enabled_1 = 1;
	        pkg_obj.clamp_enabled_1 = 1;
	        pkg_obj.limit_time_window_seconds_1 = 24*60*60; // for the day - hardcoded
	        pkg_obj.power_limit_watts_2 = pkg_power_limit; // Keeping high limit for shorter duration
	        pkg_obj.limit_enabled_2 = 1;
	        pkg_obj.clamp_enabled_2 = 1;
	        pkg_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
    	}

	/* Set the package 0 power limit */
	printf("Setting PKG 0: %iW\n", pkg_power_limit);
	ret = set_pkg_rapl_power_limit_control(0, &pkg_obj);
	if (ret != 0) {
		fprintf(stderr, "Failed to set the package power limit for node 0.\n");
	}
	else
		printf("Success!\n");
}

void do_limit_pkg1_power() {
	int domain = 0;
	int ret = -1;

	pkg_rapl_power_limit_control_t pkg_obj;
    
 	if (pkg_power_limit == -1) { // disable power limit
  		pkg_obj.power_limit_watts_1 = 0; // dummy
 	       	pkg_obj.limit_enabled_1 = 0;
 	       	pkg_obj.clamp_enabled_1 = 0;
	        pkg_obj.power_limit_watts_2 = 0; // dummy
        	pkg_obj.limit_enabled_2 = 0;
        	pkg_obj.clamp_enabled_2 = 0;
        	pkg_obj.lock_enabled = 0;
    	} else {
        	pkg_obj.power_limit_watts_1 = pkg_power_limit;
       		pkg_obj.limit_enabled_1 = 1;
        	pkg_obj.clamp_enabled_1 = 1;
        	pkg_obj.limit_time_window_seconds_1 = 24*60*60; // for the day - hardcoded
        	pkg_obj.power_limit_watts_2 = pkg_power_limit; // Keeping high limit for shorter duration
        	pkg_obj.limit_enabled_2 = 1;
        	pkg_obj.clamp_enabled_2 = 1;
        	pkg_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
    	}

	/* Set the package 0 power limit */
	printf("Setting PKG 1: %iW\n", pkg_power_limit);
	ret = set_pkg_rapl_power_limit_control(1, &pkg_obj);
	if (ret != 0) {
		fprintf(stderr, "Failed to set the package power limit for node 1.\n");
	}
	else
		printf("Success!\n");
}


void do_limit_pp0_power() {
	int i = 0;
	int domain = 0;
	uint64_t node = 0;
	int ret = -1;

	pp0_rapl_power_limit_control_t pp0_obj;

	if (pp0_power_limit == -1) { // disable power limit
		pp0_obj.power_limit_watts = 0; // dummy
		pp0_obj.limit_enabled = 0;
		pp0_obj.clamp_enabled = 0;
		pp0_obj.lock_enabled = 0;
	} else {
		pp0_obj.power_limit_watts = pp0_power_limit;
		pp0_obj.limit_enabled = 1;
		pp0_obj.clamp_enabled = 1;
		pp0_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
	}

	/* Set the pp0 power limit */
	for (i = node; i < num_node; i++) {
		ret = set_pp0_rapl_power_limit_control(i, &pp0_obj);
		if (ret != 0) {
			fprintf(stderr, "Failed to set the pp0 power limit for node %d\n",
					i);
		}
	}
}

void do_limit_dram_power() {
	int i = 0;
	int domain = 0;
	uint64_t node = 0;
	int ret = -1;

	dram_rapl_power_limit_control_t dram_obj;

	if (dram_power_limit == -1) { // disable power limit
		dram_obj.power_limit_watts = 0; //dummy
		dram_obj.limit_enabled = 0;
		dram_obj.clamp_enabled = 0;
		dram_obj.lock_enabled = 0;
	} else {
		//printf("%f\n",dram_power_limit);
		dram_obj.power_limit_watts = dram_power_limit;
		//printf("%f\n",dram_obj.power_limit_watts);
		dram_obj.limit_enabled = 1;
		dram_obj.clamp_enabled = 0;
		dram_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
	}

	/* Set the dram power limit per node */
	for (i = node; i < num_node; i++) {
		ret = set_dram_rapl_power_limit_control(i, &dram_obj);
		if (ret != 0) {
			fprintf(stderr, "Failed to set the dram power limit for node %d\n",
					i);
			perror(0);
		}
	}
}

void do_limit_dram0_power() {
	int domain = 0;
	int ret = -1;

	dram_rapl_power_limit_control_t dram_obj;

	if (dram_power_limit == -1) { // disable power limit
		dram_obj.power_limit_watts = 0; //dummy
		dram_obj.limit_enabled = 0;
		dram_obj.clamp_enabled = 0;
		dram_obj.lock_enabled = 0;
	} else {
		//printf("%f\n",dram_power_limit);
		dram_obj.power_limit_watts = dram_power_limit;
		//printf("%f\n",dram_obj.power_limit_watts);
		dram_obj.limit_enabled = 1;
		dram_obj.clamp_enabled = 0;
		dram_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
	}

	/* Set the dram power limit to node 0*/
	printf("DRAM 0 ");
	ret = set_dram_rapl_power_limit_control(0, &dram_obj);
	if (ret != 0) {
		fprintf(stderr, "Failed to set the dram power limit for node 0.\n");
		perror(0);
	}
}

void do_limit_dram1_power() {
	int domain = 0;
	int ret = -1;

	dram_rapl_power_limit_control_t dram_obj;

	if (dram_power_limit == -1) { // disable power limit
		dram_obj.power_limit_watts = 0; //dummy
		dram_obj.limit_enabled = 0;
		dram_obj.clamp_enabled = 0;
		dram_obj.lock_enabled = 0;
	} else {
		//printf("%f\n",dram_power_limit);
		dram_obj.power_limit_watts = dram_power_limit;
		//printf("%f\n",dram_obj.power_limit_watts);
		dram_obj.limit_enabled = 1;
		dram_obj.clamp_enabled = 0;
		dram_obj.lock_enabled = 0; // not enabling lock for now. disabling lock requires system reboot
	}

	/* Set the dram power limit to node 1*/
	printf("DRAM 1 ");
	ret = set_dram_rapl_power_limit_control(1, &dram_obj);
	if (ret != 0) {
		fprintf(stderr, "Failed to set the dram power limit for node 1.\n");
		perror(0);
	}
}

void usage() {
	fprintf(stdout, "\nIntel(r) Power Gadget %s\n", version);
	fprintf(stdout, "\nUsage for power monitoring: \n");
	fprintf(stdout,
			"%s [-e [sampling delay (ms) ] optional] -d [duration (sec)]\n",
			progname);
	fprintf(stdout, "Example: %s -e 1000 -d 10\n", progname);

	fprintf(stdout, "\nUsage for printing power monitoring summary: \n");
	fprintf(stdout, "%s [-s optional]\n", progname);
	fprintf(stdout, "Example: %s -s to print power monitoring summary for all the nodes\n",
			progname);

	fprintf(stdout, "\nUsage for printing power gadget output to a file: \n");
	fprintf(stdout, "%s [-f [server name] optional]\n", progname);
	fprintf(stdout, "Example: %s -f ivy will log power_gadget output to ivy.mupg.\n",
			progname);

	fprintf(stdout, "\nUsage for printing package power limit per node: \n");
	fprintf(stdout, "%s [-l optional]\n", progname);
	fprintf(stdout, "Example: %s -l to print power limit for all the nodes\n",
			progname);
	fprintf(stdout, "\nUsage for printing min max parameters per node: \n");
	fprintf(stdout, "%s [-m optional]\n", progname);
	fprintf(stdout,
			"Example: %s -m to print min max paramters for all the nodes\n",
			progname);
	fprintf(stdout, "\nUsage for limiting package power per node: \n");
	fprintf(stdout, "%s [-p [power limit per node (Watts)] optional]\n", progname);
	fprintf(stdout,
			"Example: %s -p 50 to set 50 W package power limit for all the nodes\n",
			progname);
	fprintf(stdout,
			"Example: %s -p -1 to remove package power limit from all the nodes\n",
			progname);
	fprintf(stdout, "\nUsage for limiting dram power per node: \n");
	fprintf(stdout, "%s [-r [power limit per node (Watts)] optional]\n", progname);
	fprintf(stdout,
			"Example: %s -r 50 to set 50 W dram power limit for all the nodes\n",
			progname);
	fprintf(stdout,
			"Example: %s -r -1 to remove dram power limit from all the nodes\n",
			progname);
}

int cmdline(int argc, char **argv) {
	int opt;
	uint64_t delay_ms_temp = 1000;
	char fileName[64] = {0,};

	if (argv[1] == "-r0"){
		printf("Success!\n");
	}

	while ((opt = getopt(argc, argv, "0:1:2:3:4:e:d:p:r:0:f:lmus")) != -1) {
		switch (opt) {
		case 'e':
			delay_ms_temp = atoi(optarg);
			if (delay_ms_temp > 50) {
				delay_us = delay_ms_temp * 1000;
			} else {
				fprintf(stderr, "Sampling delay must be greater than 50 ms.\n");
				return -1;
			}
			power_monitor_mode = true;
			break;
		case 'd':
			duration = atof(optarg);
			if (duration <= 0.0) {
				fprintf(stderr, "Duration must be greater than 0 seconds.\n");
				return -1;
			}
			power_monitor_mode = true;
			break;
		case 'p':
			pkg_power_limit = atof(optarg);
			pkg_power_limit_mode = true;
			break;
		case 'r':
			dram_power_limit = atof(optarg);
			dram_power_limit_mode = true;
			break;
		case '0':
			dram_power_limit = atof(optarg);
			dram0_power_limit_mode = true;
			break;
		case '1':
			dram_power_limit = atof(optarg);
			dram1_power_limit_mode = true;
			break;
		case '2':
			pkg_power_limit = atof(optarg);
			pkg0_power_limit_mode = true;
			break;
		case '3':
			pkg_power_limit = atof(optarg);
			pkg1_power_limit_mode = true;
			break;
		case '4':
			pp0_power_limit = atof(optarg);
			pp0_power_limit_mode = true;
			break;
		case 'l':
			print_power_limit = true;
			break;
		case 'm':
			print_min_max_parameters = true;
			break;
		case 'u':
			print_units = true;
			break;
		case 's':
			print_summary = true;
			break;
		case 'f':
			sprintf(fileName, "%s.mupg", optarg);
			power_log_file_handle = fopen((const char*)fileName, "w");
			break;
		case 'h':
			usage();
			exit(0);
			break;
		default:
			usage();
			return -1;
		}
	}
	return 0;
}

void sigint_handler(int signum) {
	terminate_rapl();
	exit(0);
}

int main(int argc, char **argv) {
	int i = 0;
	int ret = 0;

	progname = argv[0];

	/* Clean up if we're told to exit */
	signal(SIGINT, sigint_handler);

	/* logging to stdout by default */
	power_log_file_handle = stdout;

	if (argc < 2) {
		usage();
		terminate_rapl();
		return 0;
	}

	// First init the RAPL library
	if (0 != init_rapl()) {
		fprintf(stderr, "Init failed!\n");
		terminate_rapl();
		return MY_ERROR;
	}
	num_node = get_num_rapl_nodes_pkg();

	ret = cmdline(argc, argv);
	if (ret) {
		terminate_rapl();
		return ret;
	}

	if (print_units) {
		do_print_units();
	}

	if (power_monitor_mode) {
		do_print_energy_info();
	}

	if (pkg_power_limit_mode) {
		do_limit_pkg_power();
	}
	if (pkg0_power_limit_mode) {
		do_limit_pkg0_power();
	}
	if (pkg1_power_limit_mode) {
		do_limit_pkg1_power();
	}

	if (pp0_power_limit_mode) {
		do_limit_pp0_power();
	}

	if (dram_power_limit_mode) {
		do_limit_dram_power();
	}
	if (dram0_power_limit_mode) {
		do_limit_dram0_power();
	}
	if (dram1_power_limit_mode) {
		do_limit_dram1_power();
	}
	if (print_power_limit) {
		do_print_power_limits();
	}

	if (print_min_max_parameters) {
		do_print_min_max_parameters();
	}

	terminate_rapl();
}
