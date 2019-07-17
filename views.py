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
from models import User, Activity, Site, Action, Activist, DBModelAdder, Verification, Event
from pagination import action_pagination, event_paginator, activist_paginator
from meta import STACKEXCHANGE_CLIENT_SECRET, STACKEXCHANGE_CLIENT_ID, STACKEXCHANGE_CLIENT_KEY

STACKEXCHANGE_ADD_COMMENT_ENDPOINT = "https://api.stackexchange.com/2.2/posts/{id}/comments/add"
STACKEXCHANGE_ANSWER_API_ENDPOINT = "https://api.stackexchange.com/2.2/answers/{id}/"
STACKEXCHANGE_QUESTION_API_ENDPOINT = "https://api.stackexchange.com/2.2/questions/{id}/"
ACTION_TIMEOUT = 5
ACTIVITIES_SECTION_NAME = "activities"

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
    tab = max(int(request.args.get("tab", "1")), 1)

    base_url = url_for("activities") + "?tab=" + str(tab)
    for activity in activities:
        if activity.activity_type == tab:
            active = activity

    activists    = Action.activists(active.id)
    coordinators = Activist.coordinators(active.id)
    return render_template('activity.html',
                           section=ACTIVITIES_SECTION_NAME,
                           coordinators=coordinators,
                           activists=activists,
                           activities=activities,
                           active=active,
                           base_url=base_url,
                           tab=tab)

@application.route("/event/<event_id>")
@application.route("/event/<event_id>/")
def event(event_id):
    if g.user is None:
        return redirect(url_for('welcome'))

    event_id = int(event_id)
    event = Event.by_id(event_id)
    if event is None:
        abort(404)

    event.coordinator = User.by_id(event.created_by)
    event.attendees = Activist.attendees(event.id)
    event.valid = event.date > datetime.datetime.now()
    g.user.is_attendee = Activist.is_attendee(g.user.id, event.id)

    return render_template('event.html',
                           event=event,
                           section="events")

@application.route("/events/<event_type>")
@application.route("/events/<event_type>/")
def events(event_type):
    if g.user is None:
        return redirect(url_for('welcome'))

    if event_type not in ("upcoming", "past", "new"):
        event_type = "upcoming"
    page = max(int(request.args.get("page", "1")), 1)
    paginator = event_paginator(event_type, page)
    if paginator is not None:
        for index in range(len(paginator.items)):
            paginator.items[index].coordinator = User.by_id(paginator.items[index].created_by)
            paginator.items[index].attendees = Activist.attendees(paginator.items[index].id)

    g.user.is_coordinator = Activist.is_coordinator(g.user.id)
    return render_template('events.html',
                           section="events",
                           event_type=event_type,
                           paginator=paginator)

@application.route("/edit_event/<event_id>", endpoint="edit_event")
@application.route("/edit_event/<event_id>/", endpoint="edit_event")
def edit_event(event_id):
    if g.user is None:
        return redirect(url_for('welcome'))

    event_id = int(event_id)
    event = Event.by_id(event_id)
    if event is None:
        abort(404)

    if g.user.id != event.created_by or g.user.role != "moderator":
        abort(404)

    return render_template('edit_event.html',
                           section="events",
                           event=event)

@application.route("/activists/<activist_type>")
@application.route("/activists/<activist_type>/")
def activists(activist_type):
    if g.user is None:
        return redirect(url_for('welcome'))

    page = max(int(request.args.get("page", "1")), 1)
    if activist_type is None or activist_type not in ("activists", "coordinators"):
        activist_type = "activists"

    paginator = activist_paginator(activist_type, page)
    for index in range(len(paginator.items)):
        paginator.items[index].attended = Activist.user_attend_times(paginator.items[index].id)
        paginator.items[index].acted = Action.user_act_times(paginator.items[index].id)
        paginator.items[index].coordinated = Activist.user_coordinate_times(paginator.items[index].id)

    return render_template('activists.html',
                           paginator=paginator,
                           activist_type=activist_type,
                           section="activists")


@application.route("/no-way")
@application.route("/no-way/")
def no_way():
    return render_template('no_way.html')


@application.route("/welcome")
@application.route("/welcome/")
def welcome():
    return render_template('welcome.html')


@application.route("/actions/<activity_type>/<review_selected>", endpoint="action_list")
@application.route("/actions/<activity_type>/<review_selected>/", endpoint="action_list")
def action_list(activity_type, review_selected):
    if g.user is None:
        return redirect(url_for('welcome'))

    activity_type = int(activity_type)

    activities = Activity.all(g.site.id)
    active = None
    for activity in activities:
        if activity.activity_type == activity_type:
            active = activity

    if active is None:
        abort(404)

    page = max(int(request.args.get("page", "1")), 1)
    if review_selected is None or review_selected not in ("reviewed", "reviewing", "rejected"):
        review_selected = "reviewed"

    coordinators = Activist.coordinators(active.id)
    paginator = action_pagination(
        active,
        page,
        review_selected)
    for index in range(len(paginator.items)):
        paginator.items[index].author = User.by_id(paginator.items[index].user_id)

    return render_template('action_list.html',
                           activities=activities,
                           active=active,
                           section=ACTIVITIES_SECTION_NAME,
                           coordinators=coordinators,
                           review_selected=review_selected,
                           paginator=paginator,
                           tab=activity_type,
                           base_url=url_for(
                               "action_list",
                               activity_type=activity_type,
                               review_selected=review_selected))


@application.route("/api/verify_action/<action_id>", endpoint="verify_action")
@application.route("/api/verify_action/<action_id>/", endpoint="verify_action")
def verify_action(action_id):
    if g.user is None:
        abort(404)

    action_id = int(action_id)
    is_valid = request.args.get("valid", None)
    if action_id <= 0 or is_valid is None:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })
    try:
        is_valid = json.loads(request.args.get("valid").lower())
    except:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })
    action = Action.by_id(action_id)
    if action is None:
        return jsonify(**{
            "status": False,
            "msg": gettext("There are no action with this id.")
        })

    verification = Verification.by_user_and_action(g.user.id, action_id)
    if verification is None:
        verification = Verification(g.user.id, action_id, is_valid)
    else:
        verification.is_valid = is_valid

    pg_session = db_session()
    pg_session.add(verification)
    pg_session.commit()
    pg_session.close()

    return jsonify(**{
        "status": True,
        "msg": gettext("Action was reviewed. Thank you!")
    })


@application.route("/api/submit_action", endpoint="submit_action")
@application.route("/api/submit_action/", endpoint="submit_action")
def submit_action():
    if g.user is None:
        abort(404)

    activity_id = int(request.args.get("activity_id", "-1"))
    link = request.args.get("link", None)
    if activity_id <= 0 or link is None:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })

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

@application.route("/api/submit_event", endpoint="submit_event", methods=['GET', 'POST'])
@application.route("/api/submit_event/", endpoint="submit_event", methods=['GET', 'POST'])
def submit_event():
    if g.user is None:
        abort(404)

    if not Activist.is_coordinator(g.user.id):
        abort(404)

    data = request.get_json(force=True)
    location = ""
    description = data['description']
    meta = data['meta']
    chat = data['chat']
    date = data['date']
    event_type = data['event_type']
    title = data['title']

    mode = data['mode']

    if len(description) == 0 or\
        len(meta) == 0 or\
        len(chat) == 0 or\
        len(date) == 0 or\
        len(event_type) == 0 or\
        len(title) == 0:
        return jsonify(**{
            "status": False,
            "msg": gettext("Invalid params.")
        })
    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M")
    except:
        return jsonify(**{
            "status": False,
            "msg": gettext("Invalid date")
        })
    try:
        meta_post_id = int(re.findall('\d+', meta)[0])
    except:
        return jsonify(**{
            "status": False,
            "msg": gettext("Invalid meta url")
        })

    event = Event.by_meta_post_id(meta_post_id)
    if mode == "edit":
        if event is None:
            return jsonify(**{
                "status": False,
                "msg": gettext("There is no event with such id.")
            })

        if g.user.id != event.created_by or g.user.role != 'moderator':
            abort(404)

        event.date = date
        event.title = title
        event.description = description
        event.location = location
        event.chat_link = chat

        # We cannot change these three things:
        #event.event_type = event_type
        #event.meta_link = meta
        #event.meta_post_id = meta_post_id

        pg_session = db_session()
        pg_session.add(event)
        pg_session.commit()
        pg_session.close()
    else:
        if event is not None:
            return jsonify(**{
                "status": False,
                "msg": gettext("This event already exists")
            })

        if event_type == "meetups":
            event_type = Event.event_type_meetup
            location = data['location']
            if len(location) == 0:
                return jsonify(**{
                    "status": False,
                    "msg": gettext("Invalid params.")
                })
        else:
            event_type = Event.event_type_webcast
        event = Event(event_type, g.user.id, date, title, description, location, meta, meta_post_id, chat)
        pg_session = db_session()
        pg_session.add(event)
        pg_session.commit()
        pg_session.close()

    return jsonify(**{
        "status": True,
        "msg": gettext("Event has been added. Thank you!")
    })


@application.route("/api/attend_event/<event_id>", endpoint="attend_event")
@application.route("/api/attend_event/<event_id>/", endpoint="attend_event")
def attend_event(event_id):
    if g.user is None:
        abort(404)

    event_id = int(event_id)
    attend = request.args.get("attend", None)
    if event_id <= 0 or attend is None:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })
    try:
        attend = json.loads(attend.lower())
    except:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })

    event = Event.by_id(event_id)
    if event is None:
        return jsonify(**{
            "status": False,
            "msg": gettext("Invalid params.")
        })

    if event.date < datetime.datetime.now():
        return jsonify(**{
            "status": False,
            "msg": gettext("This event has already happened. No one cannot apply on it.")
        })

    activist = Activist.by_user_and_event(g.user.id, event.id)
    if activist is None:
        if not attend:
            return jsonify(**{
                "status": True,
                "msg": gettext("You are not on the list. No need to do anything!")
            })
        activist = Activist(g.user.id, None, event_id, Activist.role_attendee)
    else:
        activist.canceled = not attend

    activist.updated_date = datetime.datetime.now()

    pg_session = db_session()
    pg_session.add(activist)
    pg_session.commit()
    pg_session.close()

    return jsonify(**{
        "status": True,
        "msg": gettext("Your application has been saved. Thank you!")
    })

@application.route("/api/ban_user/<user_id>", endpoint="ban_user")
@application.route("/api/ban_user/<user_id>/", endpoint="ban_user")
def ban_user(user_id):
    if g.user is None or g.user.role != 'moderator':
        abort(404)
    try:
        user_id = int(user_id)
    except:
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })

    another_user = User.by_id(user_id)
    if another_user is None or (another_user.role == 'moderator' and not another_user.is_banned):
        return jsonify(**{
            "status": False,
            "msg": gettext("Wrong params")
        })
    current_status = another_user.is_banned
    another_user.is_banned = not another_user.is_banned

    pg_session = db_session()
    pg_session.add(another_user)
    pg_session.commit()
    pg_session.close()

    return jsonify(**{
        "status": True,
        "msg": gettext("The user was %s" % (
            gettext("suspended") if not current_status else gettext("unsuspended"))
        )
    })