#!/usr/bin/bash
# author nu11secur1ty
wget https://curl.haxx.se/download/curl-7.65.3.tar.gz
tar -xvf curl-7.65.3.tar.gz
cd curl-7.65.3/
	./configure
	make
	make install
exit 0;
