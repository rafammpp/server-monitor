#!/usr/bin/env python3
import requests
from utils import check_server, recheck_servers, default_ports, abs_path
import os

file = open(os.path.join(abs_path, 'server-list.dat'))

def get_port_list(line):
    if ':' in line and line.split(':')[1]:
        list_ports = line.split(':')[1].split(',')
        return [ int(p) for p in list_ports ]
    else:
        return default_ports

def get_remote_server(line):
    if ':' in line and line.split(':')[1]:
        return line.split(':')[0]
    else:
        return line

recheck_servers()

for line in file:
    line = line.strip()
    if line and line[0] != '#':
        remote_server = get_remote_server(line)
        port_list = get_port_list(line)
        check_server(remote_server, port_list)
file.close()

print('bye!')