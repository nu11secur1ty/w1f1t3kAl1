#!/usr/bin/bash
wget https://curl.haxx.se/download/curl-7.65.3.tar.gz
tar -xvf curl-7.65.3.tar.gz
cd curl-7.65.3/
	./configure
		make
		make test
	make install
	sleep 3;
git clone https://github.com/ZerBea/hcxdumptool.git
cd hcxdumptool
make 
make install
	sleep 3;
	git clone https://github.com/ZerBea/hcxtools.git
cd hcxtools
	make 
	make install
	exit 0;
