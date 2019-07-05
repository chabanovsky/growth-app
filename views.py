# encoding:utf-8
import requests
import logging
import json
import urllib
import re
from urlparse import urlparse
import datetime

from flask import Flask, jsonify, render_template, g, url_for, redirect, request, session, abort, make_response
from flask_babel import gettext, ngettext
from sqlalchemy import and_, desc
from sqlalchemy.sql import func

from meta import app as application, db, db_session, engine
from models import User, Activity, Site, Action, Activist, DBModelAdder
from pagination import action_pagination
from meta import STACKEXCHANGE_CLIENT_SECRET, STACKEXCHANGE_CLIENT_ID, STACKEXCHANGE_CLIENT_KEY

STACKEXCHANGE_ADD_COMMENT_ENDPOINT = "https://api.stackexchange.com/2.2/posts/{id}/comments/add"
STACKEXCHANGE_ANSWER_API_ENDPOINT = "https://api.stackexchange.com/2.2/answers/{id}/"
STACKEXCHANGE_QUESTION_API_ENDPOINT = "https://api.stackexchange.com/2.2/questions/{id}/"
ACTION_TIMEOUT = 5

LOGOUT_CASES = [401, 402, 403, 405, 406]
LOGOUT_MSG = gettext(
    'Your access token is not valid any more. To work with the app you need to log in again. Now you will be logged out.')


@application.before_request
def before_request():
    g.user = None
    if 'account_id' in session:
        g.user = User.query.filter_by(account_id=session['account_id']).first()
        if 'language' in session:
            g.site = Site.by_language(session['language'])
        else:
            return redirect(url_for("logout_oauth"))


@application.after_request
def after_request(response):
    db_session.close()
    db_session.remove()
    engine.dispose()

    return response

@application.route("/index.html", endpoint="activities")
@application.route("/activity", endpoint="activities")
@application.route("/", endpoint="activities")
def activities():
    if g.user is None:
        return redirect(url_for('welcome'))

    activities = Activity.all(g.site.id)

    page = max(int(request.args.get("page", "1")), 1)
    tab = max(int(request.args.get("tab", "1")), 1)
    review_selected = request.args.get("review_selected", None)
    if review_selected is None or review_selected not in ("reviewed", "reviewing", "declined"):
        review_selected = "reviewed"

    base_url = url_for("activities") + "?tab=" + str(tab)
    for activity in activities:
        if activity.activity_type == tab:
            active = activity

    paginator = action_pagination(
        active,
        page,
        review_selected)

    activists    = Action.activists(active.id)
    coordinators = Activist.coordinators(active.id)
    return render_template('activity.html',
                           section="activities",
                           coordinators=coordinators,
                           activists=activists,
                           activities=activities,
                           active=active,
                           base_url=base_url,
                           tab=tab,
                           actions_for_review=[],
                           reviewed_actions=[],
                           review_selected=review_selected,
                           paginator=paginator)

@application.route("/events")
@application.route("/events/")
def events():
    return render_template('no_way.html',
                           section="events")

@application.route("/activists")
@application.route("/activists/")
def activists():
    return render_template('no_way.html',
                           section="activists")

@application.route("/other")
@application.route("/other/")
def other():
    return render_template('no_way.html',
                           section="other")

@application.route("/no-way")
@application.route("/no-way/")
def no_way():
    return render_template('no_way.html')


@application.route("/welcome")
@application.route("/welcome/")
def welcome():
    return render_template('welcome.html')


@application.route("/api/submit_action", endpoint="submit_action")
@application.route("/api/submit_action/", endpoint="submit_action")
def submit_action():
    access_token = session.get("access_token", None)
    if g.user is None or access_token is None:
        abort(404)

    activity_id = int(request.args.get("activity_id", "-1"))
    link = request.args.get("link", None)
    if activity_id <=0 or link is None:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })

    unquoted = urllib.unquote(link)

    last = Action.last_by_user(g.user.id)
    if last is not None and (datetime.datetime.now() - last.creation_date).total_seconds() < ACTION_TIMEOUT:
        return jsonify(**{
            "status": False,
            "msg": gettext("To many actions. Take a break, please.")
        })

    adder = DBModelAdder()
    adder.start()
    if Action.is_exist(adder, activity_id, link):
        return jsonify(**{
            "status": False,
            "msg": gettext("This link for this activity has been already added.")
        })

    action = Action(g.user.id, activity_id, None, link)
    adder.add(action)
    adder.done()

    return jsonify(**{
        "status": True,
        "msg": gettext("Action was added. It will be reviewed soon. Thank you!")
    })
