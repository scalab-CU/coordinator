#include "msr_reader.h"
#include <cstdio>
#include <cstdlib>
#include <cerrno>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <cmath>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <fcntl.h>

using namespace std;

bool 	MSRReader::sInitialized = false;
double 	MSRReader::sPowerUnits = 0.0;
double 	MSRReader::sEnergyUnits = 0.0;
double 	MSRReader::sTimeUnits = 0.0;

MSRReader::MSRReader(int core_id){
	mCoreId = core_id;
	char msr_filename[MAX_MSR_FILENAME_LEN];
	sprintf(msr_filename, "/dev/cpu/%d/msr", mCoreId);
	mFd = open(msr_filename, O_RDONLY);
	if (mFd == 0) {
		extern int errno; //errno defined in <cerrno>
		throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	}
	currEnergy = &mData[0];
	prevEnergy = &mData[1];
	if (!MSRReader::sInitialized)
		MSRReader::init();
}

MSRReader::MSRReader(){
	mCoreId = 0;
	char msr_filename[MAX_MSR_FILENAME_LEN];
	sprintf(msr_filename, "/dev/cpu/%d/msr", mCoreId);
	mFd = open(msr_filename, O_RDONLY);
	if (mFd == 0) {
		extern int errno; //errno defined in <cerrno>
		throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	}
	currEnergy = &mData[0];
	prevEnergy = &mData[1];
}

MSRReader::~MSRReader(){
	if (mFd != 0) {
		close(mFd);
	}
}

MSR_DATA_T MSRReader::readMSRDate(int which){
	  if ( pread(mFd, &mTmp, sizeof(mTmp), which) != sizeof(mTmp)) {
		  throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	  }
	  return (MSR_DATA_T)mTmp;
}

void MSRReader::readEnergyData(){
	MSRData* tmp = prevEnergy;  prevEnergy=currEnergy;  currEnergy= tmp;

	currEnergy->time = MSRReaderSet::getCurrentTime();
	if ( pread(mFd, &mTmp, sizeof(mTmp), MSR_PKG_ENERGY_STATUS) != sizeof(mTmp)) {
		throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	}
	currEnergy->pkg = MSRReader::sEnergyUnits * (double)mTmp;

	if ( pread(mFd, &mTmp, sizeof(mTmp), MSR_PP0_ENERGY_STATUS)  != sizeof(mTmp)) {
		throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	};
	currEnergy->pp0 = MSRReader::sEnergyUnits * (double)mTmp;
/*
	if ( pread(mFd, &mTmp, sizeof(mTmp), MSR_PP1_ENERGY_STATUS)  != sizeof(mTmp)) {
		throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	}
	currValue->pp1 = MSRReader::sEnergyUnits * (double)mTmp;
*/
	if ( pread(mFd, &mTmp, sizeof(mTmp), MSR_DRAM_ENERGY_STATUS)  != sizeof(mTmp)) {
		throw MSRException(mCoreId, errno, __FILE__, __LINE__);
	}
	currEnergy->dram = MSRReader::sEnergyUnits * (double)mTmp;
}

void MSRReader::print(){
	cout << "[" << mCoreId << "] " << prevEnergy->pkg << "\t" << prevEnergy->pp0 << "\t";
	/* cout << currValue->pp1_energy << "\t" */
	cout << prevEnergy->dram << "\n";
}
void MSRReader::init() {
	if (!sInitialized) {
		MSRReader msr;
		MSR_DATA_T result = msr.readMSRDate(MSR_RAPL_POWER_UNIT);
		sPowerUnits = pow(0.5, (double) (result & 0xf));
		sEnergyUnits = pow(0.5, (double) ((result >> 8) & 0x1f));
		sTimeUnits = pow(0.5, (double) ((result >> 16) & 0xf));
	}
}

MSRReaderSet::MSRReaderSet(RAPLSetting* setting) {
	config = setting;
	readers = new MSRReader*[config->num_cores_sampled];
	for (int i=0; i<config->num_cores_sampled; i++){
		readers[i] = new MSRReader(config->cores_sampled[i]);
	}

	log.open(config->log_filename.c_str());
	if ( log.bad() ){
		cerr << "Create log file " << config->log_filename << " failed at " << __FILE__ << __LINE__ <<endl;
		exit(-1);
	}
}

MSRReaderSet::~MSRReaderSet(){
	if (readers) {
		for (int i=0; i<config->num_cores_sampled; i++){
			delete readers[i];
		}
		delete[] readers;
	}
	if (log.is_open())
		log.close();
}

void MSRReaderSet::doWork(){
//initial read
	currTime = getCurrentTime();
	for(int i=0; i<config->num_cores_sampled; i++) {
		readers[i]->readEnergyData();
	}
	//output the header
	log << setw(14) << "#Time";
	for(int i=0; i<config->num_cores_sampled; i++) {
		log << setw(6) << "Core" << setw(10) << "P_PKG" << setw(10) <<"P_PP0" << setw(10) << "P_DRAM";
	}
	log << endl;

	for(;;) {
		//sleep for an interval
		usleep(config->sample_interval_in_useconds);

		//read current data
		prevTime = currTime; currTime = getCurrentTime();
		for(int i=0; i<config->num_cores_sampled; i++) {
			readers[i]->readEnergyData();
		}

		//output data
		log << fixed << showpoint << setprecision(2) << setw(14) << currTime;
		for(int i=0; i<config->num_cores_sampled; i++) {
			MSRData& power = readers[i]->getPower();
			log << setw(6) << readers[i]->getCoreId() << setw(10) << power.pkg << setw(10) << power.pp0 << setw(10) << power.dram;
		}
		log << endl;
	}
}

