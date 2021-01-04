#!/usr/bin/bash
kill $(pgrep -f wpa_supplicant)
kill $(pgrep -f airmon*)
