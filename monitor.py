#!/usr/bin/env python3
import requests
from utils import check_server, recheck_servers
import os
import sys
try:
    from user_settings import default_ports, server_list_path
except ImportError:
    from default_settings import default_ports, server_list_path

file = open(server_list_path)

def get_port_list(line):
    if ':' in line and line.split(':')[1]:
        port_list = line.split(':')[1].split(',')
        return [ int(p) for p in port_list ]
    else:
        return default_ports

def get_remote_server(line):
    if ':' in line and line.split(':')[1]:
        return line.split(':')[0]
    else:
        return line

if len(sys.argv) > 1:
    s = get_remote_server(sys.argv[1])
    p = get_port_list(sys.argv[1])
    check_server(s, p)
else:
    recheck_servers()

    for line in file:
        line = line.strip()
        if line and line[0] != '#':
            remote_server = get_remote_server(line)
            port_list = get_port_list(line)
            check_server(remote_server, port_list)
    file.close()

print('bye!')