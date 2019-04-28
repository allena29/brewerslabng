#!/usr/bin/python3

import dataprovider


class brewerslab_def(dataprovider.DataProvider):

    MODULE_NAME = "brewerslab-definitions"
    DEBUG = True

    def process_path(self, dry_run, xpath, oper, old_val, new_val):
        print(xpath)


dp = brewerslab_def()
dp.connect()
