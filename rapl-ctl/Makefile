CFLAGS=-g

all: rapl_lib_shared rapl_lib_static mu_power_gadget_static

rapl_lib_shared: 
	gcc $(CFLAGS) -fpic -c msr.c cpuid.c rapl.c 
	gcc $(CFLAGS) -shared -o librapl.so msr.o cpuid.o rapl.o

rapl_lib_static: 
	gcc $(CFLAGS) -c msr.c cpuid.c rapl.c 
	ar rcs librapl.a msr.o cpuid.o rapl.o

mu_power_gadget_static: 
	gcc $(CFLAGS) mu_power_gadget.c -I. -L. -lm -o mu_power_gadget ./librapl.a

mu_power_gadget: 
	gcc $(CFLAGS) mu_power_gadget.c -I. -L. -lm -lrapl -o mu_power_gadget 

gprof: CFLAGS = -pg
gprof: all
	./mu_power_gadget -e 100 -d 60 >/dev/null 2>&1
	gprof mu_power_gadget > mu_power_gadget.gprof
	rm -f gmon.out
	make clean

clean: 
	rm -f mu_power_gadget librapl.so librapl.a msr.o cpuid.o rapl.o 
