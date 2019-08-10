#!/usr/bin/env python

# Note: This script runs Wifite from within a cloned git repo.
# The script `bin/wifite` is designed to be run after installing (from /usr/sbin), not from the cwd.
import os
from wifite import __main__
__main__.entry_point()
os.system("apt install hcxdumptool -y")
os.system("apt install hcxpcaptool -y")

