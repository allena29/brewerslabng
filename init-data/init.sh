echo "Import startup configuration"
cd /brewerslabng/init-data
for xml in *.xml
do
  module=`echo "$xml" | sed -e 's/\.xml//'`
  echo "... $module"
  sysrepocfg --import=$xml --format=xml --datastore=startup $module
done

