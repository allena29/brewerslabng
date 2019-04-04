#!/usr/bin/python3

import dataprovider

class voodoox(dataprovider.DataProvider):

    MODULE_NAME = "voodoox"
    DEBUG = True



dp = voodoox()
dp.connect()
