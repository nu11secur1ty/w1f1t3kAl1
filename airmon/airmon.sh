#!/usr/bin/bash
ifconfig -a | sed 's/[ \t].*//;/^$/d'
  exit 0;
