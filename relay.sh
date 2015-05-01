sudo kill `ps -ef | grep "sudo python pitmRelay.py" | grep -v SCREEN | grep -v grep | sed -e 's/root\s*//' -e 's/\s.*//'` 2>/dev/null
sudo screen -dmS relay sudo python pitmRelay.py
sleep 1
sudo screen -r relay
