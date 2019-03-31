#!/usr/bin/python3

import dataprovider

class integrationtest(dataprovider.DataProvider):

    MODULE_NAME = "integrationtest"
    DEBUG = True

    def process_path(self, dry_run, xpath, oper, old_val, new_val):
        print(xpath)


dp = integrationtest()
dp.connect()
