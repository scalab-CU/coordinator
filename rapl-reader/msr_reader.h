/* Read the RAPL registers on a sandybridge-ep machine                */
/* Code based on Intel RAPL driver by Zhang Rui <rui.zhang@intel.com> */
/*                                                                    */
/* The /dev/cpu/??/msr driver must be enabled and permissions set     */
/* to allow read access for this to work.                             */
/*                                                                    */
/* Compile with:   gcc -O2 -Wall -o rapl_msr rapl_msr.c -lm           */
/*                                                                    */
/* Vince Weaver -- vweaver1@eecs.utk.edu -- 16 March 2012             */
#ifndef MSR_READER_H_
#define MSR_READER_H_

#include <sys/types.h>
#include <exception>
#include <string>
#include <sstream>
#include <fstream>
#include <sys/time.h>
#include "setting.h"
using namespace std;

#define MSR_RAPL_POWER_UNIT			0x606

/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT	0x610
#define MSR_PKG_ENERGY_STATUS		0x611
#define MSR_PKG_PERF_STATUS			0x613
#define MSR_PKG_POWER_INFO			0x614

/* PP0 RAPL Domain */
#define MSR_PP0_POWER_LIMIT			0x638
#define MSR_PP0_ENERGY_STATUS		0x639
#define MSR_PP0_POLICY				0x63A
#define MSR_PP0_PERF_STATUS			0x63B

/* PP1 RAPL Domain, may reflect to uncore devices */
#define MSR_PP1_POWER_LIMIT			0x640
#define MSR_PP1_ENERGY_STATUS		0x641
#define MSR_PP1_POLICY				0x642

/* DRAM RAPL Domain */
#define MSR_DRAM_POWER_LIMIT		0x618
#define MSR_DRAM_ENERGY_STATUS		0x619
#define MSR_DRAM_PERF_STATUS		0x61B
#define MSR_DRAM_POWER_INFO			0x61C

/* RAPL UNIT BITMASK */
#define POWER_UNIT_OFFSET			0
#define POWER_UNIT_MASK				0x0F
#define ENERGY_UNIT_OFFSET			0x08
#define ENERGY_UNIT_MASK			0x1F00
#define TIME_UNIT_OFFSET			0x10
#define TIME_UNIT_MASK				0xF000

#define	MAX_MSR_FILENAME_LEN		128

typedef long long	MSR_DATA_T;
typedef struct {
	double pkg;
	double pp0;
//	double pp1;
	double dram;
	double time;
} MSRData;

class MSRException: public std::exception {
public:
	MSRException(int coreId, int errno, const char *file_name, int line_no) : mCoreId(coreId), mErrNo(errno), mLine(line_no), mFile(file_name){}
	virtual const char *what() throw() {
		stringstream buf;
		buf << "MSRException happened on core " << mCoreId << " with errno = " << mErrNo << " at " << mFile << ":" << mLine;
		return buf.str().c_str();
	}
	virtual ~MSRException() throw() {}
private:
	int mCoreId;
	int mErrNo;
	int mLine;
	string mFile;
};

class MSRReader {
public:
	MSRReader(int core_id);
	MSR_DATA_T readMSRDate(int which);
	void readEnergyData();
	~MSRReader();
	void print();
	int getCoreId() { return mCoreId; }

	MSRData& getEnergy(){
		mEnergy.pkg = currEnergy->pkg - prevEnergy->pkg;
		mEnergy.pp0 = currEnergy->pp0 - prevEnergy->pp0;
		mEnergy.dram = currEnergy->dram - prevEnergy->dram;
		mEnergy.time = currEnergy->time;
		return mEnergy;
	}
	MSRData& getPower(){
		getEnergy();
		double duration = currEnergy->time - prevEnergy->time;
		mPower.pkg = mEnergy.pkg/duration;
		mPower.pp0 = mEnergy.pp0/duration;
		mPower.dram = mEnergy.dram/duration;
		mPower.time = mEnergy.time;
		return mPower;
	}
private:
	MSRReader();
protected:
	int mCoreId;
	int	mFd;
	ssize_t mTmp;
	MSRData	mData[2];
	MSRData	mPower;
	MSRData	mEnergy;
	MSRData *currEnergy;
	MSRData *prevEnergy;
//class method and variables
public:
	static void init();
protected:
	static double 	sPowerUnits;
	static double 	sEnergyUnits;
	static double 	sTimeUnits;
	static bool	sInitialized;
};

class MSRReaderSet {
public:
	MSRReaderSet(RAPLSetting* setting);
	~MSRReaderSet();
	void doWork();
	static double getCurrentTime(){
		struct timeval ts;
		gettimeofday(&ts, NULL);
		return ts.tv_sec + 1.0e-6 * ts.tv_usec;
	}

private:
	MSRReaderSet(){};
protected:
	MSRReader	      **readers;
	RAPLSetting            *config;
	ofstream		log;
	double			prevTime;
	double			currTime;
};

#endif /* MSR_READER_H_ */
