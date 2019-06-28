import os
import sys

sys.path.append('/usr/local/share')
sys.path.append('/usr/local/share/growth_app')

def application(environ, start_response):
    os.environ['LOCALE_LANGUAGE_NAME'] = 'ru'
    print(sys.executable)
    print(sys.version)

    from growth_app import app as _application
    return _application(environ, start_response)

