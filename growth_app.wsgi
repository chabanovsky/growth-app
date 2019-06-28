import os
import sys

sys.path.append('/home')
sys.path.append('/home/growth-app')

def application(environ, start_response):
    #os.environ['STACKEXCHANGE_CLIENT_SECRET'] = environ['STACKEXCHANGE_CLIENT_SECRET']
    #os.environ['STACKEXCHANGE_CLIENT_KEY'] = environ['STACKEXCHANGE_CLIENT_KEY']
    #os.environ['STACKEXCHANGE_CLIENT_ID'] = environ['STACKEXCHANGE_CLIENT_ID']
    os.environ['LOCALE_LANGUAGE_NAME'] = 'ru'

    from growth_app import app as _application
    return _application(environ, start_response)

