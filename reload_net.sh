#!/usr/bin/bash
kill -9 $(pgrep -f wpa_supplicant)
kill -9 $(pgrep -f airmon-ng)
systemctl restart networking
