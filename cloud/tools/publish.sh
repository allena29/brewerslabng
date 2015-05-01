cd  /export/home/allena29/python/brewerslab/cloud/
cp tools/productionapp.yaml app.yaml
sudo python /export/home/allena29/python/google_appengine/appcfg.py update ./
cat tools/devapp.yaml >>app.yaml
