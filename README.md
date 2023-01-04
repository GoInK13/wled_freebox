# wled_freebox
Simple script to reduce brightness of WLED device on freebox server (using Freebox API)

## Details
It uses [freepybox](https://github.com/fstercq/freepybox)

## Installation
    pip3 install freepybox

## Add service
Create a new service :
    sudo nano /etc/systemd/system/wordClock.service

And paste the next text :

    #[Unit]
    #Description=Word clock script to set brightness
    #After=default.target
    
    #[Service]
    #ExecStart=/home/pierrot/wordClock.py
    #User=pierrot
    
    #[Install]
    #WantedBy=default.target

### Start the service 
    sudo systemctl daemon-reload
    sudo systemctl enable wordClock.service
