target = powerkit sysinfo
objects = main.o msr_reader.o setting.o sysinfo.o

powerkitOBJECT = main.o msr_reader.o setting.o
powerkit: $(powerkitOBJECT)
	g++ -O2 $(powerkitOBJECT) -o $@

sysinfoOBJECT = sysinfo.o msr_reader.o
sysinfo: $(sysinfoOBJECT)
	g++ -O2 $(sysinfoOBJECT) -o $@

$(objects): msr_reader.h

.cpp.o:

clean:
	rm -rf $(target)
	rm -rf $(objects)
