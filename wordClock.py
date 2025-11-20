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
import asyncio
from freebox_api import Freepybox
import requests
import time

PRINT_ENABLE = 0 #0: Disable print, 1:Enable
POWER_ON = 255
POWER_OFF = 5

async def main():
	# Instantiate the Freepybox class using default options.
	fbx = Freepybox(api_version="latest")

	# Connect to the freebox with default options.
	# Be ready to authorize the application on the Freebox.
	await fbx.open(host='mafreebox.freebox.fr', port=443)
	if PRINT_ENABLE==1:
		print("Connection success")

	def CheckFixIp(json):
		isFix=False
		if PRINT_ENABLE==1:
			print("\n-----\njson="+str(json))
		realName=""
		realIp=""
		try:
			if "names" in json:
				for name in json["names"]:
					if "name" in name:
						realName+=name["name"]+","
			for address in json["l3connectivities"]:
				if address["active"]==True and address["af"]=="ipv4":
					realIp=str(address["addr"])
					print("IP:"+str(realIp))
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
			fbx_lan_host = await fbx.lan.get_hosts_list()
		except Exception as e:
			if PRINT_ENABLE==1:
				print("Exception during get_hosts_list():"+str(e))
			reConnect=True
		if reConnect==True:
			await fbx.open('mafreebox.freebox.fr', port=443)
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
	await fbx.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
