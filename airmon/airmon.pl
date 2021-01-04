#!/usr/bin/perl
# Author @nu11secur1ty 2020
use strict;
use warnings;
use diagnostics;
use Term::ANSIColor;

print "\n";
print color('bold green');
print "RECOMMENDED Usage: Start the program by using (python3 w1f1t3kAl1 --help) if you want to know how to use it!\n";
print "Usage: Start the program by using (./w1f1t3kAl1 --help) if you want to know how to use it!\n";
print "After you finish execute (bash reload_net.sh)\n";
	print color('reset');
	print "\n";

print color('bold blue');
print "This is your wifi interfaces\n";
	print color('reset');

my $your_interfaces = `bash airmon/airmon.sh`;
	print color('bold yellow');
	print "$your_interfaces\n";
	print color('reset');

print color('bold red');
print "Give your wifi integrated interface?\n";
	print color('reset');

	my $target = <STDIN>;
	my $mon_stop_wifi = `airmon-ng stop $target`;
	my $mon_interface = `airmon-ng start $target`;
		
		exit 0;
