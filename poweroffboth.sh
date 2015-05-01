sudo rm ipc/handshake
ssh -lroot 192.168.1.15 sh /home/allena29/slave/stop.sh poweroff
sudo sh /home/allena29/master/stop.sh poweroff
ssh -lroot 192.168.1.15 poweroff
