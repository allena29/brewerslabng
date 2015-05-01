sudo rm ipc/handshake
ssh -lroot 192.168.1.15 sh /home/pi/brewerslab/slave/stop.sh poweroff
sudo sh /home/pi/brewerslab/master/stop.sh poweroff
ssh -lroot 192.168.1.15 poweroff
