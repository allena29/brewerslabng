#!/usr/bin/python3


import datalayer


access = datalayer.DataAccess()
access.connect()
print(access.get("/integrationtest:morecomplex/inner/leaf5"))
