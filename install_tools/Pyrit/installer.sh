#!/usr/bin/bash
# @nu11secur1ty
# Kali Linux 2020.x

apt-get update
apt-get upgrade -y
apt-get install python2.7-dev libssl-dev zlib1g-dev libpcap-dev -y
apt-get install libpcap-dev -y
  apt-get remove --purge pyrit
  rm -r /usr/local/lib/python2.7/dist-packages/cpyrit/
pip install psycopg2
pip install scapy
apt-get install python-scapy -y
echo "Downloading Pyrit"
printf '\033]2;Downloading Pyrit\a'
  git clone https://github.com/JPaulMora/Pyrit.git
  cd Pyrit
    python setup.py clean
    python setup.py build
    python setup.py install
echo "Installation finished"
printf '\033]2; Installation finished\a'
    exit 0
