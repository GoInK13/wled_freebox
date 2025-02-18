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

PRINT_ENABLE = 1 #0: Disable print, 1:Enable
POWER_ON = 255
POWER_OFF = 5

# Instantiate the Freepybox class using default options.
fbx = Freepybox()

# Connect to the freebox with default options.
# Be ready to authorize the application on the Freebox.
fbx.open('192.168.1.254')

def CheckFixIp(json):
	isFix=False
	if PRINT_ENABLE==1:
		print("\n-----\njson="+str(json))
		print("IP:"+str(json["l3connectivities"][0]["addr"]))
	realName=""
	realIp=""
	try:
		for name in json["names"]:
			realName+=name["name"]+","
		for address in json["l3connectivities"]:
			if address["active"]==True and address["af"]=="ipv4":
				realIp=str(address["addr"])
				if int(address["addr"].replace("192.168.1.",""))>200:
					isFix=True
	except Exception as e:
		if PRINT_ENABLE==1:
			print("Exception : "+str(e))
	if PRINT_ENABLE==1:
		print(str(realName)+"="+str(realIp)+"="+str(isFix))
	return isFix

def GetBrightness():
	try:
		x = requests.get("http://192.168.1.241/win")
		value=str(x.content)
		return int(value[value.index("<ac>")+4:value.index("</ac>")])
	except Exception as e:
		return 20

def CountUser():
	counterUser=0
	for jsHost in fbx_lan_host:
		if jsHost["active"]==True:
			if CheckFixIp(jsHost)==False:
				counterUser+=1
	return counterUser

counterUserOld=0
oldValue=GetBrightness()

reConnect=False

while True:
	try:
		fbx_lan_host = fbx.lan.get_hosts_list()
	except Exception as e:
		reConnect=True
	if reConnect==True:
		fbx.open('192.168.1.254')
		time.sleep(10)
		reConnect=False
		pass
	try:
		counterUser=CountUser()
	except Exception as e:
		if PRINT_ENABLE==1:
			print("Exception during counter user:"+str(e))
		counterUser=0
	if PRINT_ENABLE==1:
		print("Number user = "+str(counterUser))
	if counterUserOld!=counterUser:
		if counterUser>0:
			if oldValue<=20:
				oldValue=255
			if str(GetBrightness())!='0':
				try:
					x = requests.get('http://192.168.1.241/win&A='+str(oldValue))
				except Exception as e:
					pass
		else:
			oldValue=GetBrightness()
			try:
				x = requests.get('http://192.168.1.241/win&A='+str(POWER_OFF))
			except Exception as e:
				pass
		counterUserOld=counterUser
	time.sleep(30)

# Properly close the session.
fbx.close()
