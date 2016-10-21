#ifndef SETTING_H_
#define SETTING_H_

#include <string>
using namespace std;

#define USECOND_PER_SECOND	1000000L
#define	MAX_CORES_ARGMENT_LEN	128
#define DEFAULT_LOG_FILENAME	"rapl.log"

void show_usage(const char *prog);

struct RAPLSetting {
public:
        bool    output_to_console;
	long	sample_interval_in_useconds;
	string 	log_filename;
	int	*cores_sampled;
	int	num_cores_sampled;
public:
	RAPLSetting();
	void initFromArguments(int argc, char*argv[]);
	~RAPLSetting();
	void print();
	void parseListOfCores(char *list);
};

#endif /* SETTING_H_ */
