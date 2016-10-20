#include "msr_reader.h"
#include "setting.h"
#include <cstring>
#include <string>
#include <iostream>
#include <cstdlib>
#include <exception>

#include <setjmp.h>
#include <signal.h>

using namespace std;

static jmp_buf env;

//sig_int: a signal handler for signal SIG_INT
static void sig_int(int signo) {
	longjmp(env, 1);
}

static void catch_sigint(void)
{
	struct sigaction act;

	memset(&act, 0, sizeof(struct sigaction));
	act.sa_handler = sig_int;
	if( sigaction(SIGINT, &act, NULL) < 0 ) {
		perror("unable to catch SIGINT");
		exit(1);
	}
}

int main(int argc, char *argv[]){

//parse command argument
	RAPLSetting setting;
	setting.initFromArguments(argc, argv);
	setting.print();

//define a set of MSRReaders
	MSRReaderSet readers(&setting);

//setup signal
	if (setjmp(env) == 0) {
		catch_sigint();
		readers.doWork();
	} else {
//cleanup and release resources
		cerr << "Exiting from RAPLReader..." << endl;
	}
}


