from behave import given, when, then, step
import pexpect


def send_cli(cli_to_send):
    a=2
#
#
##  GENERIC
#
#

@when("we send the following CLI")
def step_impl(context):
    send_cli(context.text)

#
#
##  MASH 
#
#

@given("We set the HLT temperature for the mash to 69.0 degC")
def step_impl(context):
    pass
