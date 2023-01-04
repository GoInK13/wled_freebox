#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# How it works?
## This checks for devices connected.
## If there is nobody home, it automatically reduce
## brightness of WLED modules
#To launch as service :
# pip3 install freepybox
# sudo nano /etc/systemd/system/wordClock.service
###
#[Unit]
#Description=Word clock script to set brightness
#After=default.target

#[Service]
#ExecStart=/home/pierrot/wordClock.py
#User=pierrot

#[Install]
#WantedBy=default.target
###
# sudo systemctl daemon-reload
# sudo systemctl enable wordClock.service


# Import the freepybox package.
from freepybox import Freepybox
import requests
import time

# Instantiate the Freepybox class using default options.
fbx = Freepybox()

# Connect to the freebox with default options. 
# Be ready to authorize the application on the Freebox.
fbx.open('192.168.1.254')

counterUserOld=0
while True:
	try:
		fbx_lan_host = fbx.lan.get_hosts_list()
	except Exception as e:
		fbx.open('192.168.1.254')
	counterUser=0
	for jsHost in fbx_lan_host:
		if jsHost["active"]==True:
#			print("jsHost="+str(jsHost["names"]))
#			print(str(jsHost))
			counterUser+=1
	if counterUserOld!=counterUser:
		if counterUser>4:
			x = requests.get('http://192.168.1.241/win&A=255')
		else:
			x = requests.get('http://192.168.1.241/win&A=20')
		counterUserOld=counterUser
	time.sleep(30)

# Properly close the session.
fbx.close()
