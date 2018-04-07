#!/bin/bash
date;
cd ~/server-monitor;
git pull origin master;
python3.6 monitor.py;
