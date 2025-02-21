# wled_freebox
Simple script to reduce brightness of WLED device on freebox server (using Freebox API)

## Details
It uses [freepybox](https://github.com/fstercq/freepybox)

## Installation on debian  

```
git clone https://github.com/GoInK13/wled_freebox.git
cd wled_freebox
sudo apt update
sudo apt install python3-pip
python3 -m venv venv-wordclock
venv-wordclock/bin/pip3 install freebox-api
venv-wordclock/bin/pip3 install requests
```

## Test

```
source venv-wordclock/bin/activate
python3 wordClock.py
```

## Add service

Create a new service :

```
sudo nano /etc/systemd/system/wordClock.service
```

And paste the next text :

```
[Unit]
Description=Word clock script to set brightness
After=default.target

[Service]
WorkingDirectory=/home/pierrot/servers/wled_freebox
ExecStart=/home/pierrot/servers/wled_freebox/venv-wordclock/bin/python3 /home/pierrot/servers/wled_freebox/wordClock.py
#Restart=on-failure
User=pierrot

[Install]
WantedBy=default.target
```

### Start the service 

```
sudo systemctl daemon-reload
sudo systemctl enable wordClock.service
sudo systemctl start wordClock.service
```
