# encoding:utf-8
import requests
import logging
import json
import urllib
import re
from urlparse import urlparse

from flask import Flask, jsonify, render_template, g, url_for, redirect, request, session, abort, make_response
from flask_babel import gettext, ngettext
from sqlalchemy import and_, desc
from sqlalchemy.sql import func

from meta import app as application, db, db_session, engine
from models import User, Activity, Site
from meta import STACKEXCHANGE_CLIENT_SECRET, STACKEXCHANGE_CLIENT_ID, STACKEXCHANGE_CLIENT_KEY

STACKEXCHANGE_ADD_COMMENT_ENDPOINT = "https://api.stackexchange.com/2.2/posts/{id}/comments/add"
STACKEXCHANGE_ANSWER_API_ENDPOINT = "https://api.stackexchange.com/2.2/answers/{id}/";
STACKEXCHANGE_QUESTION_API_ENDPOINT = "https://api.stackexchange.com/2.2/questions/{id}/";

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

@application.route("/index.html", endpoint="activity")
@application.route("/activity", endpoint="activity")
@application.route("/", endpoint="activity")
def activity():
    if g.user is None:
        return redirect(url_for('welcome'))

    activities = Activity.all(g.site.id)
    tab = max(int(request.args.get("tab", "1")), 1)
    base_url = url_for("activity") + "?tab=" + str(tab)
    return render_template('activity.html',
                           activities=activities,
                           base_url=base_url,
                           tab=tab,
                           paginator=None)


@application.route("/no-way")
@application.route("/no-way/")
def no_way():
    return render_template('no_way.html')


@application.route("/welcome")
@application.route("/welcome/")
def welcome():
    return render_template('welcome.html')

