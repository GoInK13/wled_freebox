#!/usr/bin/env python3

# Import the freepybox package.
import asyncio
from freebox_api import Freepybox
import requests
import time

# Import mqtt
from paho.mqtt import client as mqtt_client

# Configure MQTT server
broker = '192.168.1.203'
port = 1883
topic = "python/freeByGoInK/1/wifiClients"
# Generate a Client ID with the publish prefix.
client_id = f'teslamateImmich'
username = 'MQTT'
password = 'MQTT'

PRINT_ENABLE = 1 #0: Disable print, 1:Enable
POWER_ON = 255
POWER_OFF = 5

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    #client = mqtt_client.Client(client_id)
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"{msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 500:
            break

async def main(client):
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
			isFix=True
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
					print("+1:"+str(jsHost))
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
		if False and counterUserOld!=counterUser:
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
		result = client.publish(topic, counterUser)
		# result: [0, 1]
		status = result[0]
		if status == 0:
			print("Send "+str(counterUser)+" to topic "+str(topic))
		else:
			print("Failed to send message "+str(counterUser)+" to topic "+str(topic))
		time.sleep(30)

	# Properly close the session.
	await fbx.close()


def run():
    client = connect_mqtt()
    client.loop_start()
    # Connect to freebox
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(client))
    loop.close()
    client.loop_stop()





if __name__ == '__main__':
    run()

