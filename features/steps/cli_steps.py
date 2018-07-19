from behave import given, when, then, step
import sys
import pexpect
import os


def send_cli(context, cli_to_send):
    context.cli_last_result = []
    if not context.cli:
        print('Opening CLI Client on %s' % (str(context.port)))
        os.environ['PYCONF_PORT'] = str(context.port)
        os.environ['TERM'] = 'dumb'
        os.chdir(context.basedir)
        print (os.getcwd())
        context.cli = pexpect.spawn('./launch --cli')
        #context.cli = pexpect.spawn('./launch --cli', cwd=context.basedir)
        context.cli.expect('localhost[%>]')
        print (context.cli.before)

    for line in cli_to_send.split('\n'):
        print ('Sending CLI line %s' % (line))
        context.cli.send(line + '\n')
        context.cli.expect('localhost[%>]')
        context.cli_last_result.append(context.cli.before)
        print ('Response from sending %s' % (context.cli_last_result[-1]))


@when("we send the following CLI")
def step_impl(context):
    send_cli(context, context.text)
