from behave import given, when, then, step
import sys
import pexpect
import time
import os


@when("we open the command line interface")
def step_impl(context):
    os.chdir(context.basedir)
    context.cli = pexpect.spawn('bash -ci ./cli', cwd=context.basedir)

@then("we should be presented with a welcome prompt containing")
def step_impl(context):
    context.cli.expect(context.text, timeout=2)
