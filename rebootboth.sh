sudo rm ipc/*
ssh -lroot 192.168.1.15 "sh /home/pi/brewerslab/slave/stop.sh reboot"
sudo sh /home/pi/brewerslab/master/stop.sh reboot
