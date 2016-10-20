#include "setting.h"
#include <unistd.h>
#include <vector>
#include <iostream>
#include <cstdlib>

using namespace std;

void show_usage(char *prog) {
	cerr << "usage: " << endl;
	cerr << "\t" << prog << " [-f log_file] [-s sample_interval_in_seconds] [-c core_id,core_id,...]" << endl;
	cerr << "\t" << prog << " -h" << endl;
	exit(-1);
}

RAPLSetting::RAPLSetting() {
	sample_interval_in_useconds = 1 * USECOND_PER_SECOND;
	log_filename				= DEFAULT_LOG_FILENAME;
	num_cores_sampled			= 1;
	cores_sampled				= new int[num_cores_sampled];
	cores_sampled[0]			= 0;
}

RAPLSetting::~RAPLSetting(){
	delete[] cores_sampled;
}

void RAPLSetting::parseListOfCores(char *list) {
	vector<string> cores;
	string s(list);
	size_t beginPos = 0;
	size_t foundPos = 0;
	cout << "start: s = " << s << " begin = " << beginPos << " found=" << foundPos << endl;
	while (foundPos != s.npos) {
		foundPos = s.find(',', beginPos);
		cout << "start: s = " << s << " begin = " << beginPos << " found=" << foundPos << endl;
		string strId;
		if (foundPos == s.npos) {
			strId = s.substr(beginPos);
			beginPos = s.npos;
		}
		else{
			strId = s.substr(beginPos, foundPos-beginPos);
			beginPos = foundPos + 1;
		}
		cout << "substr = " << strId << endl;
		cores.push_back(strId);
	}

	if (cores.size() > 0 ) {
		cores_sampled = new int[cores.size()];
		for (int i=0; i<cores.size(); i++) {
			cores_sampled[i] = atoi(cores[i].c_str());
		}
		num_cores_sampled = cores.size();
	}
}

void RAPLSetting::initFromArguments(int argc, char*argv[]) {
	int option;

	while ( (option = getopt(argc, argv, "hf:s:c:")) != -1) {
		switch (option) {
		case 'f':
			log_filename = optarg;
			break;
		case 's':
			sample_interval_in_useconds = long (atof(optarg) * USECOND_PER_SECOND);
			break;
		case 'c':
			parseListOfCores(optarg);
			break;
		case 'h':
			show_usage(argv[0]);
			break;
		default:
			show_usage(argv[0]);
			break;
		}
	}
}

void RAPLSetting::print(){
	cout << "RAPL Settings:" << endl;
	cout << "\tsample_interval_in_useconds = "  << sample_interval_in_useconds << endl;
	cout << "\tlog_filename                = "  << log_filename << endl;
	cout << "\tnum_cores_sampled           = "  << num_cores_sampled << endl;
	cout << "\tnum_cores_sampled           = ";
	for (int i=0; i<num_cores_sampled; i++) {
		cout << cores_sampled[i] << " ";
	}
	cout << endl;
}

