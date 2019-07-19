import logging

from datetime import datetime
from sqlalchemy import and_, not_, desc, asc
from sqlalchemy.sql import func, case
from flask_sqlalchemy import Pagination
from flask import g, request, session

from meta import db
from models import Action, Verification, Event, Activist, User, Activity

DEFAULT_QUESTION_NUMBER_LIMIT = 1000
DEFAULT_QUESTIONS_PER_PAGE = 10
NEEDED_REVIEW_NUM = 1


def action_pagination(activity, page_num, reviewed, per_page=DEFAULT_QUESTIONS_PER_PAGE):
    subquery = db.session.query(
        Verification.action_id.label("action_id"),
        func.sum(case([(Verification.is_valid == True, 1), ], else_=-1)).label("balance"),
        func.count(Verification.action_id).label("total")
    ).group_by(Verification.action_id).subquery()

    if reviewed == "reviewed":
        action_query = db.session.query(Action).join(subquery, Action.id == subquery.c.action_id).filter(
            and_(subquery.c.balance > 0, subquery.c.total >= NEEDED_REVIEW_NUM))

    elif reviewed == "reviewing":
        middle_query = db.session.query(Action.id).join(subquery, Action.id == subquery.c.action_id).filter(
            subquery.c.total >= NEEDED_REVIEW_NUM)

        my_verifications = db.session.query(Verification.action_id).filter(Verification.user_id == g.user.id).group_by(Verification.action_id)

        action_query = db.session.query(Action).filter(~Action.id.in_(middle_query)).filter(~Action.id.in_(my_verifications))
    else:
        action_query = db.session.query(Action).join(subquery, Action.id == subquery.c.action_id).filter(
            and_(subquery.c.balance < 0, subquery.c.total >= NEEDED_REVIEW_NUM))

    action_query = action_query.filter(Action.activity_id == activity.id).order_by(desc(Action.creation_date)).distinct()
    return pagination_helper(page_num, per_page, action_query)


def pagination_helper(page_num, per_page, the_query):
    total = the_query.count()
    items = the_query.offset((page_num-1)*per_page).limit(per_page).all()
    p = Pagination(the_query, page_num, per_page, total, items)
    return p


def event_paginator(event_type, site_id, page_num, per_page=DEFAULT_QUESTIONS_PER_PAGE):
    if event_type == "upcoming":
        event_query = db.session.query(Event).filter(
            Event.site_id == site_id, Event.date >= datetime.now()).order_by(desc(Event.date)).distinct()
    elif event_type == "past":
        event_query = db.session.query(Event).filter(
            Event.site_id == site_id, Event.date < datetime.now()).order_by(desc(Event.date)).distinct()
    else:
        return None

    return pagination_helper(page_num, per_page, event_query)


def activist_paginator(activist_type, site_id, page_num, per_page=DEFAULT_QUESTIONS_PER_PAGE):
    if activist_type == "activists":
        attendee_query = db.session.query(User.id.label('id')).join(
            Activist, User.id == Activist.user_id).join(Event).filter(
            Activist.role == Activist.role_attendee, Event.site_id==site_id).group_by(User.id)

        action_query = db.session.query(User.id.label('id')).join(
            Action, User.id == Action.user_id).join(Activity).filter(
            Activity.site_id == site_id).group_by(User.id)

        union_query = action_query.union_all(attendee_query).subquery()

        activist_query = db.session.query(User).join(
            union_query, User.id == union_query.c.id).distinct()
    else:
        activist_query = db.session.query(User).join(Activist).join(Activity).filter(
            Activist.role == Activist.role_coordinator, Activity.site_id == site_id).order_by(
            asc(Activist.creation_date)).distinct()

    return pagination_helper(page_num, per_page, activist_query)
