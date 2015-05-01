
mkdir /currentdata
echo "Mount Tmpfs"
mount -t tmpfs -o size=2m tmpfs /currentdata

mkdir /currentdata/temps
