
mkdir /currentdata
echo "Mount Tmpfs"
mount -t tmpfs -o size=2m tmpfs /currentdata
mkdir /currentdata/temps
chown beer:beer /currentdata/temps
screen -dmS mcstRx1 python mcastTempRecevier.py

