#!/usr/bin/env python3

import subprocess
import time
import sys

def restart_network():
    """Restart NetworkManager and network services"""
    print("Restarting network...")
    
    # Stop NetworkManager
    subprocess.run(['systemctl', 'stop', 'NetworkManager'])
    time.sleep(2)
    
    # Start NetworkManager
    subprocess.run(['systemctl', 'start', 'NetworkManager'])
    time.sleep(1)
    
    # Restart wpa_supplicant
    subprocess.run(['systemctl', 'restart', 'wpa_supplicant'])
    
    print("Network restarted successfully!")

def restart_interface(interface="wlan0"):
    """Restart specific network interface"""
    print(f"Restarting {interface}...")
    
    # Bring down
    subprocess.run(['ip', 'link', 'set', interface, 'down'])
    time.sleep(1)
    
    # Bring up
    subprocess.run(['ip', 'link', 'set', interface, 'up'])
    
    print(f"{interface} restarted!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Restart specific interface
        restart_interface(sys.argv[1])
    else:
        # Restart NetworkManager
        restart_network()
