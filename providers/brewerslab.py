#!/usr/bin/python3

import dataprovider

class brewerslab(dataprovider.DataProvider):

    MODULE_NAME = "brewerslab"
    DEBUG = True

    def process_path(self, dry_run, xpath, oper, old_val, new_val):
        print(xpath)


dp = brewerslab()
dp.connect()
