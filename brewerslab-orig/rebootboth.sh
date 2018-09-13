sudo rm ipc/*
ssh 192.168.1.15 "sh /home/beer/brewerslab/slave/stop.sh reboot"
sudo sh /home/beer/brewerslab/master/stop.sh reboot
