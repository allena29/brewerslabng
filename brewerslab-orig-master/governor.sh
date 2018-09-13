
ping 192.168.1.13 -c 5

if [ -f "simulator" ]
then
	echo "$1 Governor (Simulator Mode)"
	who=`whoami`
	cmd="python"
	cmd2="screen"
else
	echo "$1 Governor"
	who=" root"
	cmd="sudo python"
	cmd2="sudo screen"
fi

kill `ps -ef | grep "$cmd pitmGovernor.py" | grep -v SCREEN | grep -v grep | sed -e "s/$who\s*//" -e 's/\s.*//'` 2>/dev/null

if [ "$1" = "kill" ]
then
 exit 
fi

$cmd2 -dmS governor $cmd pitmGovernor.py
if [ "$1" = "" ]
then 
	sleep 1
	$cmd2 -r governor
fi
	
