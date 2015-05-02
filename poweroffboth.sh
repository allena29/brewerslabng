sudo rm ipc/handshake
ssh 192.168.1.15 "sudo sh /home/beer/brewerslab/slave/stop.sh poweroff"
sudo sh /home/beer/brewerslab/master/stop.sh poweroff
ssh -lroot 192.168.1.15 poweroff
