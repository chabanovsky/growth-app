import sys
import os

from meta import *
from models import *
from auth import *
from views import *
from oauth import *
from filters import *

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from database import init_db
        if str(sys.argv[1]) == "--init_db":
            init_db()

    app.run()
