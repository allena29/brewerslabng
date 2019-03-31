#!/usr/bin/python3

import dataprovider
import sysrepo as sr

"""
This example works although very tivial
netconf-console --user netconf --password netconf --host 127.0.0.1 --port 830 --get-config

  <morecomplex xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
    <inner>
      <leaf5>fsf</leaf5>
    </inner>
  </morecomplex>


netconf-console --user netconf --password netconf --host 127.0.0.1 --port 830 --get-config
  <morecomplex xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
    <inner>
      <leaf5>fsf</leaf5>
    </inner>
    <nonconfig>hello</nonconfig>
  </morecomplex>
"""

class integrationtestOper(dataprovider.DataProvider):

    MODULE_NAME = "integrationtest"
    DEBUG = True

    def refresh_oper_values(self, oper_val_dict, xpath):
        print("refresh oper_values for ", xpath)
        oper_val_dict['/nonconfig'] = ('hello', sr.SR_STRING_T)


dp = integrationtestOper()
dp.connect_oper('/integrationtest:morecomplex')
