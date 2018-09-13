	echo "$1 LedMatrix"
	who=" root"
	cmd="sudo python"
	cmd2="sudo screen"

kill `ps -ef | grep "$cmd pitmLedMatrix.py" | grep -v SCREEN | grep -v grep | sed -e "s/$who\s*//" -e 's/\s.*//'` 2>/dev/null
if [ "$1" = "kill" ]
then
 exit
fi
$cmd2 -dmS matrix $cmd pitmLedMatrix.py
if [ "$1" = "" ]
then 
	sleep 1
	$cmd2 -r matrix
fi
	
