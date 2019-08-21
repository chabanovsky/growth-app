Growth app is an app for Stack Overflow activists who want to bring  collaborative knowledge sharing to their language.

## How To Install

1. Check out code from GitHub to any folder.
2. Create a symbolic link `ln -s /path/to/your/folder/growth-app/ /home/growth_app`. It means that we assume that the root directory of the project is "/home/growth_app". If you want to user another directory, take a look at the *growth-app/growth_app.wsgi*, and *growth-app/growth_app.conf*.
3. Set up apache according the app folder and the version of apache. You can find growth_app.conf for `/home/growth_app` and for apache 2.2.
4. You need apache web server, mod_wsgi, postgres 9+ installed.
5. Install Flask and Flask's modules

    pip install Flask    
    pip install Flask-Babel    
    pip install Flask-SQLAlchemy   
    pip install Flask-OpenID  
    
6. Login to postgres.

    psql -U postgres -h localhost -d template1
    
7. Create a user and a database.

    CREATE USER your user;   
    CREATE DATABASE growth_app;   
    GRANT ALL PRIVILEGES ON DATABASE growth_app TO your_user;   

  <sup>*</sup> If you cannot log in as a postgres [see this](http://stackoverflow.com/questions/15791406/).
  <sup>**</sup> If there are issues with auth [see this](http://stackoverflow.com/a/30052923/564240).


8. Create a local_settings.py file in the growth-app folder with following variables

    STACKEXCHANGE_CLIENT_SECRET = "secret"   
    STACKEXCHANGE_CLIENT_KEY = "key"   
    STACKEXCHANGE_CLIENT_ID = id   

    FLASK_SECRET_KEY = 'key'   
    PG_NAME_PASSWORD = "name:pass"   
    
9. Execute `python growth_app.py --init_db`. This command creates database tables according the models. 
10. Execute `python growth_app.py --load_sites`. This command loads 'site_conf.json' and fills the Site database table. 
11. Execute `python growth_app.py --load_activities`. This command loads activities and activists from activities_conf.json.

This was it. Now it should work. If it does not, please ping @NicolasChabanovsky in [The Terminal](https://chat.stackexchange.com/rooms/84778/the-terminal).     