sudo rm ipc/handshake
ssh 192.168.1.15 "sh /home/beer/brewerslab/slave/stop.sh poweroff"
sudo sh /home/beer/brewerslab/master/stop.sh poweroff
