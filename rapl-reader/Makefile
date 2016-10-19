target = rapl
objects = main.o msr_reader.o setting.o
rapl-ivy: $(objects)
	g++ -o $@ $(objects)
rapl: $(objects)
	g++ -o $@ $(objects)
$(objects): msr_reader.h

clean:
	rm -rf $(target)
	rm -rf $(objects)
