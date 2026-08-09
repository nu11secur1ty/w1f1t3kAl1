#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pyrit Installer - Fixed for Python 3.13+
Handles compatibility issues with modern Python versions
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
import re
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

class PyritInstallerFixed:
    def __init__(self):
        self.os_type = self.detect_os()
        self.is_root = os.geteuid() == 0
        self.python_version = self.get_python_version()
        self.temp_dir = None

    def detect_os(self):
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
        return system

    def get_python_version(self):
        """Get Python version as tuple"""
        version = sys.version_info
        return f"{version.major}.{version.minor}"

    def print_header(self):
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}{' ' * 15}Pyrit Installer (Python {self.python_version} Fixed){Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.CYAN}OS Detected: {self.os_type}{Colors.NC}")
        print(f"{Colors.CYAN}Python Version: {self.python_version}{Colors.NC}")
        print(f"{Colors.CYAN}Root Access: {'Yes' if self.is_root else 'No'}{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

    def run_command(self, command, capture_output=False, check=False):
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
            else:
                result = subprocess.run(command, shell=True)
                return None, None, result.returncode
        except Exception as e:
            return None, str(e), 1

    def install_dependencies(self):
        print(f"{Colors.YELLOW}[1/6] Installing system dependencies...{Colors.NC}")
        
        if self.os_type == 'debian':
            packages = (
                "git python3 python3-pip python3-dev "
                "build-essential libssl-dev libpcap-dev "
                "libsqlite3-dev libgcrypt-dev cmake "
                "python3-scapy"  # Include scapy from apt
            )
            cmd = f"apt-get update && apt-get install -y {packages}"
            _, _, code = self.run_command(cmd)
            if code == 0:
                print(f"{Colors.GREEN}✓ Dependencies installed.{Colors.NC}")
                return True
        elif self.os_type == 'arch':
            packages = "git python python-pip base-devel openssl libpcap sqlite libgcrypt cmake"
            cmd = f"pacman -Sy --noconfirm {packages}"
            _, _, code = self.run_command(cmd)
            if code == 0:
                print(f"{Colors.GREEN}✓ Dependencies installed.{Colors.NC}")
                return True
        
        print(f"{Colors.YELLOW}⚠ Could not auto-install dependencies. Continuing...{Colors.NC}")
        return True

    def install_python_deps(self):
        print(f"{Colors.YELLOW}[2/6] Installing Python dependencies...{Colors.NC}")
        
        # Use older compatible versions
        deps = [
            "psycopg2-binary",
            "scapy"
        ]
        
        success = True
        for dep in deps:
            print(f"{Colors.CYAN}  Installing {dep}...{Colors.NC}")
            # Try with --no-cache-dir to avoid issues
            _, _, code = self.run_command(f"pip3 install --no-cache-dir {dep}")
            if code != 0:
                print(f"{Colors.RED}✗ Failed to install {dep}{Colors.NC}")
                success = False
            else:
                print(f"{Colors.GREEN}✓ {dep} installed.{Colors.NC}")
        
        return success

    def patch_pyrit_source(self, pyrit_dir):
        """Apply patches to make Pyrit compatible with Python 3.13+"""
        print(f"{Colors.YELLOW}[3/6] Patching Pyrit source for Python {self.python_version}...{Colors.NC}")
        
        patches_applied = 0
        
        # Patch 1: Fix Py_InitModule (deprecated in Python 3)
        file_path = os.path.join(pyrit_dir, "cpyrit", "_cpyrit_cpu.c")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace Py_InitModule with PyModule_Create
            if 'Py_InitModule' in content:
                content = content.replace(
                    'Py_InitModule("_cpyrit_cpu", CPyritCPUMethods)',
                    'PyModule_Create(&CPyritCPUMethods)'
                )
                patches_applied += 1
            
            # Fix return statements in init function
            content = re.sub(
                r'if\s*\((.*?)\)\s*{\s*return;\s*}',
                r'if (\1) { PyErr_Print(); return NULL; }',
                content
            )
            
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"{Colors.GREEN}✓ Patched _cpyrit_cpu.c{Colors.NC}")

        # Patch 2: Fix Python 3.13 type initialization
        file_path = os.path.join(pyrit_dir, "cpyrit", "cpyrit_cpu.h")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add modern type initialization if missing
            if 'PyType_Ready' not in content:
                # Add type declaration fixes
                content = content.replace(
                    'PyObject_HEAD_INIT(NULL)',
                    'PyObject_HEAD_INIT(&PyType_Type)'
                )
                
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"{Colors.GREEN}✓ Patched cpyrit_cpu.h{Colors.NC}")
                patches_applied += 1

        return patches_applied > 0

    def install_pyrit_from_source(self):
        """Install Pyrit with compatibility fixes"""
        print(f"{Colors.YELLOW}[4/6] Installing Pyrit from source...{Colors.NC}")
        
        # Check if already installed
        _, _, code = self.run_command("which pyrit", capture_output=True)
        if code == 0:
            print(f"{Colors.GREEN}✓ Pyrit is already installed.{Colors.NC}")
            return True

        self.temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            # Clone
            print(f"{Colors.CYAN}  Cloning Pyrit repository...{Colors.NC}")
            self.run_command("git clone https://github.com/JPaulMora/Pyrit.git")
            os.chdir("Pyrit")

            # Apply patches
            self.patch_pyrit_source(".")

            # Build with Python 3.13 compatibility flags
            print(f"{Colors.CYAN}  Building Pyrit...{Colors.NC}")
            os.environ['CFLAGS'] = '-Wno-error=implicit-function-declaration -Wno-error=incompatible-pointer-types'
            self.run_command("python3 setup.py clean")
            self.run_command("python3 setup.py build")

            # Install
            print(f"{Colors.CYAN}  Installing Pyrit...{Colors.NC}")
            self.run_command("sudo python3 setup.py install")

            # Verify
            _, _, code = self.run_command("which pyrit", capture_output=True)
            if code == 0:
                print(f"{Colors.GREEN}✓ Pyrit installed successfully!{Colors.NC}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠ Pyrit installed but 'pyrit' not in PATH.{Colors.NC}")
                print(f"{Colors.YELLOW}  Try: export PATH=\$PATH:/usr/local/bin{Colors.NC}")
                return True

        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.NC}")
            return False
        finally:
            os.chdir(original_dir)
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def install_alternative(self):
        """Alternative: Use a forked/updated version or install via pip"""
        print(f"{Colors.YELLOW}[5/6] Trying alternative installation method...{Colors.NC}")
        
        # Try pip installation (if available)
        _, _, code = self.run_command("pip3 install pyrit", capture_output=True)
        if code == 0:
            print(f"{Colors.GREEN}✓ Pyrit installed via pip!{Colors.NC}")
            return True
        
        # Try using pyrit from Kali repos if on Debian
        if self.os_type == 'debian':
            print(f"{Colors.CYAN}  Trying apt install pyrit...{Colors.NC}")
            _, _, code = self.run_command("apt-get install -y pyrit")
            if code == 0:
                print(f"{Colors.GREEN}✓ Pyrit installed from apt!{Colors.NC}")
                return True
        
        # Try the old stable release
        print(f"{Colors.CYAN}  Trying Pyrit stable release...{Colors.NC}")
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        try:
            # Use older release that works with Python 3.10/3.11
            self.run_command(
                "wget https://github.com/JPaulMora/Pyrit/archive/refs/tags/v0.5.0.tar.gz"
            )
            self.run_command("tar -xzf v0.5.0.tar.gz")
            os.chdir("Pyrit-0.5.0")
            
            # Try to build with compatibility flags
            os.environ['CFLAGS'] = '-Wno-error'
            self.run_command("python3 setup.py build")
            self.run_command("sudo python3 setup.py install")
            
            _, _, code = self.run_command("which pyrit", capture_output=True)
            if code == 0:
                print(f"{Colors.GREEN}✓ Pyrit stable version installed!{Colors.NC}")
                return True
        except:
            pass
        finally:
            os.chdir("/tmp")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        
        return False

    def verify_installation(self):
        """Verify and display installation info"""
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}{' ' * 20}Verification{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        
        # Check pyrit
        stdout, _, code = self.run_command("which pyrit", capture_output=True)
        if code == 0:
            print(f"{Colors.GREEN}✓ Pyrit is installed at: {stdout}{Colors.NC}")
            version, _, _ = self.run_command("pyrit --version", capture_output=True)
            if version:
                print(f"{Colors.CYAN}  Version: {version[:100]}{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}✗ Pyrit not found.{Colors.NC}")
            return False

    def show_manual_fix(self):
        """Show manual fix instructions"""
        print(f"\n{Colors.YELLOW}Manual Fix for Python 3.13:{Colors.NC}")
        print("1. Install older Python version (3.10 or 3.11):")
        print("   sudo apt-get install python3.10 python3.10-dev python3.10-venv")
        print("2. Create virtual environment:")
        print("   python3.10 -m venv pyrit_env")
        print("   source pyrit_env/bin/activate")
        print("3. Install Pyrit:")
        print("   git clone https://github.com/JPaulMora/Pyrit.git")
        print("   cd Pyrit")
        print("   pip install psycopg2-binary scapy")
        print("   python setup.py build")
        print("   python setup.py install")
        print("\nOr use Docker:")
        print("   docker pull kalilinux/kali-linux-docker")
        print("   docker run -it kalilinux/kali-linux-docker /bin/bash")
        print("   apt-get update && apt-get install -y pyrit")

    def main(self):
        self.print_header()
        
        if not self.is_root:
            print(f"{Colors.RED}✗ Run as root: sudo python3 {sys.argv[0]}{Colors.NC}")
            sys.exit(1)

        # Check Python version
        major, minor = map(int, self.python_version.split('.'))
        if major >= 3 and minor >= 13:
            print(f"{Colors.YELLOW}⚠ Python 3.13 detected - may have compatibility issues{Colors.NC}")
            print(f"{Colors.YELLOW}  Using compatibility patches...{Colors.NC}")

        # Install
        self.install_dependencies()
        self.install_python_deps()
        
        success = self.install_pyrit_from_source()
        
        if not success:
            print(f"{Colors.YELLOW}⚠ Source installation failed. Trying alternative...{Colors.NC}")
            success = self.install_alternative()
        
        # Verify
        verified = self.verify_installation()
        
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        if verified:
            print(f"{Colors.GREEN}✓ Pyrit installed successfully!{Colors.NC}")
            print(f"{Colors.CYAN}  Test with: pyrit list_cores{Colors.NC}")
        else:
            print(f"{Colors.RED}✗ Installation failed.{Colors.NC}")
            self.show_manual_fix()
        
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

if __name__ == "__main__":
    installer = PyritInstallerFixed()
    installer.main()
