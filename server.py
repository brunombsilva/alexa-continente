#!/usr/bin/env python

import click
import logging
import sys
import signal
import json
from selenium import webdriver
from continente import Continente
import application

@click.command()
@click.option('--skill-id', help='Alexa Skill Id', required=True)
@click.option('--username', help='Continente Online username', required=True)
@click.option('--password', help='Continente Online password', required=True)
@click.option('--port', help='Application port', default= 4000)
@click.option('--chrome', help='Chrome driver URL', default= 'http://chrome:4444/wd/hub')
@click.option('--debug', help='Debug mode', default= False)
@click.option('--skill-schema', help='Skill Language Model', required=True, default= 'skill.json')
def server(skill_id, username, password, port, chrome, debug, skill_schema):
    global continente

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stderr))

    if debug:
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
	logging.getLogger('flask_ask').setLevel(logging.DEBUG)
	logger.setLevel(logging.DEBUG)

    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1200x600')
    options.add_argument('headless')
    driver = webdriver.Remote(
	chrome, 
	desired_capabilities=options.to_capabilities()
    )

    json_data=open(skill_schema).read()
    data = json.loads(json_data)
    schema = {'id': skill_id, 'languageModel': data['languageModel'] }
    products = {}
    for i, t in enumerate(schema['languageModel']['types']):
	if t['name'] == 'LIST_OF_PRODUCTS':
	    for j, v in enumerate(t['values']):
		products[v['id']] = v['name']['value']

    continente = Continente(username= username, password= password, driver= driver, products= products)
    continente.login_async()

    app = application.create(continente= continente, logger= logger, schema= schema)
    app.run('0.0.0.0', port, debug=False)

def exit_gracefully(a, b):
    print('Exiting...')
    sys.stdout.flush()
    continente.dispose()
    
if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    server(auto_envvar_prefix='CONTINENTE')
