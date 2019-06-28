import csv
import os
import re
from datetime import datetime

import logging
from meta import db, db_session, engine, STACKOVERFLOW_HOSTNAME
from models import User
from utils import print_progress_bar, print_association_setting
from sqlalchemy.sql import func
from sqlalchemy import and_, not_, select, exists, delete

MINIMUM_VIEW_COUNT_TO_ADD = 30


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    db.create_all()


