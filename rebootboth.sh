sudo rm ipc/*
ssh -lroot 192.168.1.15 "sh /home/allena29/slave/stop.sh reboot"
sudo sh /home/allena29/master/stop.sh reboot
