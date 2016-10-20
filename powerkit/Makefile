target = powerkit
objects = main.o msr_reader.o setting.o

powerkit: $(objects)
	g++ -O2 $(objects) -o $@

sysinfo: sysinfo.o msr_reader.o
	g++ -O2 $+ -o sysinfo
	
$(objects): msr_reader.h

clean:
	rm -rf $(target)
	rm -rf $(objects)
