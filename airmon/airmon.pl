#!/usr/bin/perl
use strict;
use warnings;
use diagnostics;
use Term::ANSIColor;

print color('bold blue');
print "This is your wifi interfaces\n";
	print color('reset');

my $your_interfaces = `iwconfig`;
	print color('bold yellow');
	print "$your_interfaces\n";
	print color('reset');

print color('bold red');
print "Give your wifi integrated interface?\n";
	my $target = <STDIN>;
	my $mon_stop_wifi = `airmon-ng stop $target`;
	my $mon_interface = `airmon-ng start $target`;
		print color('reset');
	exit 0;
