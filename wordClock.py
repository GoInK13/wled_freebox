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

def CheckFixIp(json):
	isFix=False
	print("\n-----\njson="+str(json))
	print("IP:"+str(json["l3connectivities"][0]["addr"]))
	realName=""
	realIp=""
	for name in json["names"]:
		realName+=name["name"]+","
	for address in json["l3connectivities"]:
		if address["active"]==True and address["af"]=="ipv4":
			realIp=str(address["addr"])
			if int(address["addr"].replace("192.168.1.",""))>200:
				isFix=True
	print(str(realName)+"="+str(realIp)+"="+str(isFix))
	return isFix

def GetBrightness():
	try:
		x = requests.get("http://192.168.1.241/win")
		value=str(x.content)
		return int(value[value.index("<ac>")+4:value.index("</ac>")])
	except Exception as e:
		return 20

counterUserOld=0
oldValue=GetBrightness()

while True:
	try:
		fbx_lan_host = fbx.lan.get_hosts_list()
	except Exception as e:
		fbx.open('192.168.1.254')
	counterUser=0
	for jsHost in fbx_lan_host:
		if jsHost["active"]==True:
			if CheckFixIp(jsHost)==False:
				counterUser+=1
	print("Number user = "+str(counterUser))
	if counterUserOld!=counterUser:
		if counterUser>0:
			if oldValue<=20:
				oldValue=255
			try:
				x = requests.get('http://192.168.1.241/win&A='+str(oldValue))
			except Exception as e:
				pass
		else:
			oldValue=GetBrightness()
			try:
				x = requests.get('http://192.168.1.241/win&A=20')
			except Exception as e:
				pass
		counterUserOld=counterUser
	time.sleep(30)

# Properly close the session.
fbx.close()
