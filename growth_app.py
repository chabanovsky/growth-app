import sys
import os
import datetime

from meta import *
from models import *
from auth import *
from views import *
from oauth import *
from filters import *

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from database import init_db, load_sites, load_site_posts, load_activities
        if str(sys.argv[1]) == "--init_db":
            init_db()
        if str(sys.argv[1]) == "--load_sites":
            load_sites("sites_conf.json")

        if str(sys.argv[1]) == "--load_activities":
            load_activities("activities_conf.json")

        if str(sys.argv[1]) == "--load_posts":
            start_date = os.environ.get("START_DATE", None)
            if start_date is not None:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d") # "2019-12-31"
            load_site_posts(start_date)

        quit()


    app.run()
