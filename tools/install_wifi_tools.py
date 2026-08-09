#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WiFi Tools Installer
Installs: Pyrit, hcxdumptool, hcxpcapngtool
Author: Auto Installer
Version: 1.0
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
import urllib.request
import json
from pathlib import Path

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'

class WiFiToolsInstaller:
    def __init__(self):
        self.os_type = self.detect_os()
        self.is_root = os.geteuid() == 0
        self.temp_dir = None
        self.installed_tools = {}
        
    def detect_os(self):
        """Detect the operating system"""
        system = platform.system().lower()
        
        if system == 'linux':
            try:
                with open('/etc/os-release', 'r') as f:
                    os_info = f.read()
                    if 'ubuntu' in os_info.lower() or 'debian' in os_info.lower():
                        return 'debian'
                    elif 'fedora' in os_info.lower() or 'rhel' in os_info.lower():
                        return 'redhat'
                    elif 'arch' in os_info.lower() or 'manjaro' in os_info.lower():
                        return 'arch'
            except:
                pass
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        else:
            return 'unknown'

    def print_header(self):
        """Print installation header"""
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.BLUE}{Colors.BOLD}    WiFi Security Tools Installer{Colors.NC}")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.CYAN}OS Detected: {self.os_type}{Colors.NC}")
        print(f"{Colors.CYAN}Root Access: {'Yes' if self.is_root else 'No'}{Colors.NC}")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")

    def check_root(self):
        """Check if running as root"""
        if not self.is_root:
            print(f"{Colors.RED}✗ This script must be run as root!{Colors.NC}")
            print(f"{Colors.YELLOW}Please run: sudo python3 {sys.argv[0]}{Colors.NC}")
            return False
        return True

    def run_command(self, command, capture_output=False, check=True):
        """Run a system command"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
            else:
                result = subprocess.run(command, shell=True, check=check)
                return None, None, result.returncode
        except subprocess.CalledProcessError as e:
            return None, str(e), e.returncode

    def install_dependencies(self):
        """Install system dependencies"""
        print(f"{Colors.YELLOW}Installing system dependencies...{Colors.NC}")
        
        packages = {
            'debian': 'git python3 python3-pip python3-dev build-essential libssl-dev libpcap-dev libsqlite3-dev libgcrypt-dev libxml2-dev cmake libcurl4-openssl-dev libz-dev',
            'redhat': 'git python3 python3-pip python3-devel gcc make openssl-devel libpcap-devel sqlite-devel libgcrypt-devel libxml2-devel cmake curl-devel zlib-devel',
            'arch': 'git python python-pip python-setuptools base-devel openssl libpcap sqlite libgcrypt libxml2 cmake curl zlib',
            'macos': 'git python3 cmake openssl libpcap'
        }
        
        if self.os_type in packages:
            if self.os_type == 'debian':
                cmd = f"apt-get update && apt-get install -y {packages['debian']}"
            elif self.os_type == 'redhat':
                cmd = f"yum install -y {packages['redhat']}"
            elif self.os_type == 'arch':
                cmd = f"pacman -Sy --noconfirm {packages['arch']}"
            elif self.os_type == 'macos':
                cmd = f"brew install {packages['macos']}"
            else:
                print(f"{Colors.RED}No package manager found for {self.os_type}{Colors.NC}")
                return False
            
            _, _, code = self.run_command(cmd)
            if code == 0:
                print(f"{Colors.GREEN}✓ Dependencies installed successfully{Colors.NC}")
                return True
            else:
                print(f"{Colors.RED}✗ Failed to install dependencies{Colors.NC}")
                return False
        return True

    def install_hcxtools(self):
        """Install hcxdumptool and hcxtools"""
        print(f"{Colors.YELLOW}Installing hcxdumptool and hcxtools...{Colors.NC}")
        
        # Try package manager first
        if self.os_type == 'debian':
            cmd = "apt-get install -y hcxdumptool hcxtools"
            _, _, code = self.run_command(cmd)
            if code == 0:
                print(f"{Colors.GREEN}✓ hcxdumptool and hcxtools installed via package manager{Colors.NC}")
                self.installed_tools['hcxdumptool'] = True
                self.installed_tools['hcxpcapngtool'] = True
                return True
        
        # Build from source if package manager fails
        print(f"{Colors.YELLOW}Building from source...{Colors.NC}")
        self.temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            # Install hcxtools
            print(f"{Colors.CYAN}Installing hcxtools...{Colors.NC}")
            self.run_command("git clone https://github.com/ZerBea/hcxtools.git")
            os.chdir("hcxtools")
            self.run_command("make")
            self.run_command("make install")
            os.chdir("..")
            
            # Install hcxdumptool
            print(f"{Colors.CYAN}Installing hcxdumptool...{Colors.NC}")
            self.run_command("git clone https://github.com/ZerBea/hcxdumptool.git")
            os.chdir("hcxdumptool")
            self.run_command("make")
            self.run_command("make install")
            os.chdir("..")
            
            print(f"{Colors.GREEN}✓ hcxtools and hcxdumptool installed from source{Colors.NC}")
            self.installed_tools['hcxdumptool'] = True
            self.installed_tools['hcxpcapngtool'] = True
            return True
            
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to build from source: {e}{Colors.NC}")
            return False
        finally:
            os.chdir(original_dir)
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def install_pyrit(self):
        """Install Pyrit from source"""
        print(f"{Colors.YELLOW}Installing Pyrit...{Colors.NC}")
        
        # Check if already installed
        _, _, code = self.run_command("which pyrit", capture_output=True)
        if code == 0:
            print(f"{Colors.GREEN}✓ Pyrit is already installed{Colors.NC}")
            self.installed_tools['pyrit'] = True
            return True
        
        # Install Python dependencies
        print(f"{Colors.CYAN}Installing Python dependencies...{Colors.NC}")
        self.run_command("pip3 install --upgrade pip")
        self.run_command("pip3 install psycopg2-binary scapy")
        
        # Clone and build Pyrit
        self.temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            print(f"{Colors.CYAN}Cloning Pyrit repository...{Colors.NC}")
            self.run_command("git clone https://github.com/JPaulMora/Pyrit.git")
            os.chdir("Pyrit")
            
            print(f"{Colors.CYAN}Building Pyrit...{Colors.NC}")
            self.run_command("python3 setup.py build")
            self.run_command("python3 setup.py install")
            
            # Verify installation
            _, _, code = self.run_command("which pyrit", capture_output=True)
            if code == 0:
                print(f"{Colors.GREEN}✓ Pyrit installed successfully{Colors.NC}")
                self.installed_tools['pyrit'] = True
                return True
            else:
                print(f"{Colors.YELLOW}⚠ Pyrit installed but may not be in PATH{Colors.NC}")
                print(f"{Colors.YELLOW}Try: export PATH=$PATH:/usr/local/bin{Colors.NC}")
                return True
                
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to install Pyrit: {e}{Colors.NC}")
            return False
        finally:
            os.chdir(original_dir)
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def verify_installation(self):
        """Verify all tools are installed"""
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.BLUE}{Colors.BOLD}    Verification Results{Colors.NC}")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        
        tools = {
            'pyrit': 'Pyrit',
            'hcxdumptool': 'hcxdumptool',
            'hcxpcapngtool': 'hcxpcapngtool'
        }
        
        all_installed = True
        
        for cmd, name in tools.items():
            stdout, stderr, code = self.run_command(f"which {cmd}", capture_output=True)
            if code == 0:
                version_cmd = f"{cmd} --version" if cmd != 'hcxdumptool' else f"{cmd} --version"
                version, _, _ = self.run_command(version_cmd, capture_output=True)
                print(f"{Colors.GREEN}✓ {name} - INSTALLED{Colors.NC}")
                if version:
                    print(f"{Colors.CYAN}  Version: {version[:50]}...{Colors.NC}")
                self.installed_tools[cmd] = True
            else:
                print(f"{Colors.RED}✗ {name} - NOT INSTALLED{Colors.NC}")
                all_installed = False
        
        return all_installed

    def show_help(self):
        """Show help information"""
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.BOLD}Manual Installation Instructions:{Colors.NC}")
        print(f"{Colors.YELLOW}Pyrit:{Colors.NC}")
        print("  https://github.com/JPaulMora/Pyrit/wiki")
        print(f"{Colors.YELLOW}hcxdumptool:{Colors.NC}")
        print("  apt install hcxdumptool")
        print(f"{Colors.YELLOW}hcxpcapngtool:{Colors.NC}")
        print("  apt install hcxtools")
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")

    def main(self):
        """Main installation process"""
        self.print_header()
        
        # Check root access
        if not self.check_root():
            sys.exit(1)
        
        # Install dependencies
        if not self.install_dependencies():
            print(f"{Colors.RED}Failed to install dependencies. Continuing anyway...{Colors.NC}")
        
        # Install hcxtools
        self.install_hcxtools()
        
        # Install Pyrit
        self.install_pyrit()
        
        # Verify installation
        success = self.verify_installation()
        
        # Show results
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        if success:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TOOLS INSTALLED SUCCESSFULLY!{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some tools were not installed{Colors.NC}")
            self.show_help()
        
        print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
        print(f"{Colors.GREEN}Installation completed!{Colors.NC}")

if __name__ == "__main__":
    installer = WiFiToolsInstaller()
    installer.main()
