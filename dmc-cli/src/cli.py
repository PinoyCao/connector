import json
import click
import settings
from dmcserver import twisted
from agent import Agent, ConApi


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
def dmc_agent():
    agent = Agent()
    agent.run()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--host', default='0.0.0.0', help='ip that server listens on')
@click.option('--port', default=5000, help='port that server listens on')
def dmc_server(**kwargs):
    twisted.run(kwargs.get('host', 'utf-8'), port=kwargs.get('port', 'utf-8'), debug=True)
    # app.run(host=kwargs.get('host', 'utf-8'), port=kwargs.get('port', 'utf-8'), threaded=True)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--full', help='show a full list of devices, removed devices included', is_flag=True, default=False)
@click.option('--head', help='show the first connected device only', is_flag=True, default=False)
def dmc_devices(**kwargs):
    response = ConApi(settings.DMC_API_URI).get_list()
    if response:
        dlist = response.json().get('devices')
        if dlist:  # not empty
            if(kwargs.get('full')):
                print json.dumps(dlist, sort_keys=True, indent=4)
            else:
                # filter removed devices
                dlist = [d for d in dlist if not d['is_removed']]
                if(kwargs.get('head')):
                    print json.dumps(dlist[0], sort_keys=True, indent=4) if dlist else []
                else:
                    print json.dumps(dlist, sort_keys=True, indent=4)
        else:
            print "No Device connected."
