#!/bin/sh
cd /export/home/allena29/python/brewerslab/cloud
cp tools/productionapp.yaml app.yaml
cat tools/devapp.yaml >>app.yaml
