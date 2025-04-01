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
topic_list = "python/freeByGoInK/1/wifiClientsList"
topic_listAll = "python/freeByGoInK/1/wifiClientsListAll"
# Generate a Client ID with the publish prefix.
client_id = f'teslamateImmich'
username = 'MQTT'
password = 'MQTT'

PRINT_ENABLE = 0 #0: Disable print, 1:Enable
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

async def main(client):
    # Instantiate the Freepybox class using default options.
    fbx = Freepybox(api_version="latest")

    # Connect to the freebox with default options.
    # Be ready to authorize the application on the Freebox.
    await fbx.open(host='mafreebox.freebox.fr', port=443)
    if PRINT_ENABLE==1:
        print("Connection success")

    def GetClientFromJson(json):
        isFix=False
        if PRINT_ENABLE==1:
            print("\n-----\njson="+str(json))
            print("IP:"+str(json["l3connectivities"][0]["addr"]))
        realName=""
        try:
            __find_start = str(json).find("'primary_name'")+17
            __find_stop  = str(json).find("'", __find_start)
            realName=str(json)[__find_start:__find_stop]
        except Exception as e:
            realName="Unknown"
            if PRINT_ENABLE==1:
                print("Exception : "+str(e))
        try:
            __find_start = str(json).find("'192.168.1")+1
            __find_stop  = str(json).find("'", __find_start)
            realIp=str(json)[__find_start:__find_stop]
        except Exception as e:
            realIp="192.168.1.255"
            if PRINT_ENABLE==1:
                print("Exception : "+str(e))
        if int(realIp.replace("192.168.1.",""))>=200:
            isFix=True
        return isFix,realIp,realName

    def GetClients():
        clients = []
        for jsHost in fbx_lan_host:
            if jsHost["active"]==True:
                is_ip_fix, ip_number, ip_name = GetClientFromJson(jsHost)
                clients.append({is_ip_fix, ip_number, ip_name})
                if PRINT_ENABLE==1:
                    print("+1:"+str(clients[-1]))
        return clients

    reConnect=False

    while True:
        clientsAll=[]
        clients=[]
        counterUser=0
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
            clientsAll=GetClients()
            clients=[clientsFalse for clientsFalse in clientsAll if False in clientsFalse]
            counterUser=len(clients)
        except Exception as e:
            if PRINT_ENABLE==1:
                print("Exception during counter user:"+str(e))
            counterUser=0
        if PRINT_ENABLE==1:
            print("users : "+str(clients))
        result = client.publish(topic, counterUser)
        status = result[0]
        result = client.publish(topic_listAll, str(clientsAll))
        result = client.publish(topic_list, str(clients))
        if PRINT_ENABLE==1:
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

