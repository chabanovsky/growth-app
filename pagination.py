import logging

from sqlalchemy import and_, not_, desc
from sqlalchemy.sql import func
from flask_sqlalchemy import Pagination
from flask import g, request, session

from meta import db
from models import Action

DEFAULT_QUESTION_NUMBER_LIMIT = 1000
DEFAULT_QUESTIONS_PER_PAGE = 30


def action_pagination(activity, page_num, reviewed, per_page=DEFAULT_QUESTIONS_PER_PAGE):
    if reviewed == "reviewed":
        action_query = db.session.query(Action).filter(
            and_(
                Action.valid == True,
                Action.verified == True,
                Action.activity_id==activity.id)
        )
    elif reviewed == "reviewing":
        action_query = db.session.query(Action).filter(
            and_(
                Action.verified == False,
                Action.activity_id==activity.id)
        )
    else:
        action_query = db.session.query(Action).filter(
            and_(
                Action.valid == False,
                Action.verified == True,
                Action.activity_id==activity.id)
        )

    action_query = action_query.order_by(desc(Action.creation_date)).distinct()
    return pagination_helper(page_num, per_page, action_query)


def pagination_helper(page_num, per_page, action_query):
    total = action_query.count()
    items = action_query.offset((page_num-1)*per_page).limit(per_page).all()
    p = Pagination(action_query, page_num, per_page, total, items)
    return p