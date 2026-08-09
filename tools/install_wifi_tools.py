#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Official Pyrit Installer
Follows the guide at: https://github.com/JPaulMora/Pyrit/wiki
Installs: Pyrit (main module) and its dependencies.
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path

# ANSI colors for better readability
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class PyritInstaller:
    def __init__(self):
        self.os_type = self.detect_os()
        self.is_root = os.geteuid() == 0
        self.temp_dir = None

    def detect_os(self):
        """Detect the operating system (Focus on Linux)"""
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
        return system  # 'linux', 'darwin' (macOS), or 'windows'

    def print_header(self):
        """Print installation header"""
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}{' ' * 15}Official Pyrit Installer{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.CYAN}OS Detected: {self.os_type}{Colors.NC}")
        print(f"{Colors.CYAN}Root Access: {'Yes' if self.is_root else 'No'}{Colors.NC}")
        print(f"{Colors.YELLOW}Following guide: https://github.com/JPaulMora/Pyrit/wiki{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

    def run_command(self, command, capture_output=False, check=True):
        """Run a system command"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
            else:
                subprocess.run(command, shell=True, check=check)
                return None, None, 0
        except subprocess.CalledProcessError as e:
            return None, str(e), e.returncode

    def install_dependencies_linux(self):
        """Install system dependencies for Linux (Debian/Ubuntu focus)"""
        print(f"{Colors.YELLOW}[1/5] Installing system dependencies...{Colors.NC}")
        
        # Packages from official wiki: python-dev, openssl-dev, gcc, git, etc.
        debian_packages = (
            "git python3 python3-pip python3-dev "
            "build-essential libssl-dev libpcap-dev "
            "libsqlite3-dev libgcrypt-dev libxml2-dev "
            "cmake libcurl4-openssl-dev libz-dev"
        )
        
        if self.os_type == 'debian':
            cmd = f"apt-get update && apt-get install -y {debian_packages}"
            _, _, code = self.run_command(cmd)
            if code == 0:
                print(f"{Colors.GREEN}✓ Dependencies installed successfully.{Colors.NC}")
                return True
            else:
                print(f"{Colors.RED}✗ Failed to install dependencies.{Colors.NC}")
                return False
        elif self.os_type == 'arch':
            arch_packages = "git python python-pip base-devel openssl libpcap sqlite libgcrypt libxml2 cmake curl zlib"
            cmd = f"pacman -Sy --noconfirm {arch_packages}"
            _, _, code = self.run_command(cmd)
            return code == 0
        else:
            print(f"{Colors.YELLOW}⚠ Automatic dependency install not supported for {self.os_type}.{Colors.NC}")
            print("Please install: git, python3, python3-pip, openssl-dev, and build-essential.")
            return True  # Assume user will install manually

    def install_python_dependencies(self):
        """Install Python dependencies: psycopg2 and scapy (as per wiki)"""
        print(f"{Colors.YELLOW}[2/5] Installing Python dependencies (psycopg2, scapy)...{Colors.NC}")
        
        # Official wiki recommends: pip install psycopg2-binary scapy
        deps = ["psycopg2-binary", "scapy"]
        success = True
        for dep in deps:
            print(f"{Colors.CYAN}  Installing {dep}...{Colors.NC}")
            _, _, code = self.run_command(f"pip3 install {dep}")
            if code != 0:
                # Fallback for Debian systems if pip fails
                if dep == "scapy" and self.os_type == 'debian':
                    print(f"{Colors.YELLOW}  Trying fallback: apt-get install python3-scapy{Colors.NC}")
                    _, _, code = self.run_command("apt-get install -y python3-scapy")
                if code != 0:
                    print(f"{Colors.RED}✗ Failed to install {dep}{Colors.NC}")
                    success = False
            else:
                print(f"{Colors.GREEN}✓ {dep} installed.{Colors.NC}")
        return success

    def install_pyrit_from_source(self):
        """Clone, build, and install Pyrit from official Git repository"""
        print(f"{Colors.YELLOW}[3/5] Installing Pyrit from source (Git)...{Colors.NC}")
        
        # Check if Pyrit is already installed
        _, _, code = self.run_command("which pyrit", capture_output=True)
        if code == 0:
            print(f"{Colors.GREEN}✓ Pyrit is already installed. Skipping build.{Colors.NC}")
            return True

        # Create temp directory for cloning
        self.temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            # Official git clone command
            print(f"{Colors.CYAN}  Cloning from https://github.com/JPaulMora/Pyrit.git...{Colors.NC}")
            self.run_command("git clone https://github.com/JPaulMora/Pyrit.git")
            os.chdir("Pyrit")

            # Build and install as per wiki
            print(f"{Colors.CYAN}  Building Pyrit...{Colors.NC}")
            self.run_command("python3 setup.py clean")
            self.run_command("python3 setup.py build")
            
            print(f"{Colors.CYAN}  Installing Pyrit...{Colors.NC}")
            self.run_command("sudo python3 setup.py install")

            # Verify installation
            _, _, code = self.run_command("which pyrit", capture_output=True)
            if code == 0:
                print(f"{Colors.GREEN}✓ Pyrit installed successfully!{Colors.NC}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠ Pyrit installed but 'pyrit' command not found in PATH.{Colors.NC}")
                print("  Try: export PATH=$PATH:/usr/local/bin")
                return True  # Installation likely succeeded

        except Exception as e:
            print(f"{Colors.RED}✗ Error during Pyrit installation: {e}{Colors.NC}")
            return False
        finally:
            os.chdir(original_dir)
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def verify_installation(self):
        """Final verification"""
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}{' ' * 20}Verification{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        
        # Check for pyrit command
        stdout, _, code = self.run_command("which pyrit", capture_output=True)
        if code == 0:
            print(f"{Colors.GREEN}✓ Pyrit is installed at: {stdout}{Colors.NC}")
            # Try to get version
            version, _, _ = self.run_command("pyrit --version", capture_output=True)
            if version:
                print(f"{Colors.CYAN}  Version info: {version[:100]}{Colors.NC}")
        else:
            print(f"{Colors.RED}✗ Pyrit command not found.{Colors.NC}")
            print("  Try running: sudo python3 setup.py install from the Pyrit source directory.")
            return False

        # Check for optional GPU modules (CUDA/OpenCL) - just informative
        print(f"\n{Colors.YELLOW}Optional GPU Acceleration:{Colors.NC}")
        print("  For CUDA/OpenCL support, install additional modules:")
        print("  - https://github.com/JPaulMora/Pyrit/wiki/Setup-CUDA-and-OpenCL")
        
        return True

    def show_manual_instructions(self):
        """Show manual installation instructions if automatic fails"""
        print(f"\n{Colors.YELLOW}Manual Installation Steps:{Colors.NC}")
        print("1. Install dependencies:")
        print("   sudo apt-get install git python3 python3-pip python3-dev build-essential libssl-dev")
        print("2. Install Python packages:")
        print("   sudo pip3 install psycopg2-binary scapy")
        print("3. Clone and install Pyrit:")
        print("   git clone https://github.com/JPaulMora/Pyrit.git")
        print("   cd Pyrit")
        print("   python3 setup.py build")
        print("   sudo python3 setup.py install")
        print(f"\n{Colors.CYAN}Full guide: https://github.com/JPaulMora/Pyrit/wiki{Colors.NC}")

    def main(self):
        """Main installation process"""
        self.print_header()
        
        # Check root
        if not self.is_root:
            print(f"{Colors.RED}✗ This script must be run as root (sudo).{Colors.NC}")
            sys.exit(1)

        # Step 1: System deps
        if not self.install_dependencies_linux():
            print(f"{Colors.RED}Failed to install system dependencies.{Colors.NC}")
            self.show_manual_instructions()
            sys.exit(1)

        # Step 2: Python deps
        if not self.install_python_dependencies():
            print(f"{Colors.YELLOW}⚠ Some Python dependencies failed. Continuing...{Colors.NC}")

        # Step 3: Install Pyrit
        if not self.install_pyrit_from_source():
            print(f"{Colors.RED}✗ Pyrit installation failed.{Colors.NC}")
            self.show_manual_instructions()
            sys.exit(1)

        # Step 4: Verify
        success = self.verify_installation()
        
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        if success:
            print(f"{Colors.GREEN}✓ Pyrit has been successfully installed!{Colors.NC}")
            print("  You can now use: pyrit list_cores")
            print("  For GPU support, see the optional modules guide.")
        else:
            print(f"{Colors.RED}✗ Installation may not be complete.{Colors.NC}")
            self.show_manual_instructions()
        
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

if __name__ == "__main__":
    installer = PyritInstaller()
    installer.main()
