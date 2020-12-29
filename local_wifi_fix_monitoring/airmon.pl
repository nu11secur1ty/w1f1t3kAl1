#!/usr/bin/perl
use strict;
use warnings;
use diagnostics;

print "This is your wifi interfaces\n";
my $your_interfaces = `iwconfig`;
	print "$your_interfaces\n";
print "Give your wifi integrated interface?\n";
	my $target = <STDIN>;
	my $mon_stop_wifi = `airmon-ng stop $target`;
	my $mon_interface = `airmon-ng start $target`;
	exit 0;
