# encoding:utf-8
import requests
import json
import csv
import os
import re
import sys
from datetime import datetime
import time

import logging
from meta import db, db_session, engine, STACKEXCHANGE_CLIENT_KEY
from models import User, Site, SiteInfo, Post, DBModelAdder, Activity
from flask import jsonify
from utils import print_progress_bar
from sqlalchemy.sql import func
from sqlalchemy import and_, not_, select, exists, delete

SE_SITEINFO_ENDPOINT = 'https://api.stackexchange.com/2.2/info'
SE_POST_ENDPOINT     = 'https://api.stackexchange.com/2.2/posts'
SE_ANSWER_ENDPOINT   = 'https://api.stackexchange.com/2.2/answers/{ids}'
SE_QUESTION_ENDPOINT = 'https://api.stackexchange.com/2.2/questions/{ids}'
SE_POST_FILTER       = '!bN4djS-XBrJSha'

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    db.create_all()


def load_site_info(site_id, site_api_name):
    params = {
        "key": STACKEXCHANGE_CLIENT_KEY,
        "site": site_api_name,
        "preview": "false"
    }
    r = requests.get(SE_SITEINFO_ENDPOINT, data=params)
    try:
        data = json.loads(r.text)
    except:
        return jsonify(**{
            "error": r.text
        })

    if data.get("items", None) is None:
        return "Cannot find 'items' prop. %s" % str(data)

    for item in data["items"]:
        if item.get("total_users", None) is not None:
            total_users = int(item["total_users"])

        if item.get("total_badges", None) is not None:
            total_badges = int(item["total_badges"])

        if item.get("total_votes", None) is not None:
            total_votes = int(item["total_votes"])

        if item.get("total_comments", None) is not None:
            total_comments = int(item["total_comments"])

        if item.get("total_answers", None) is not None:
            total_answers = int(item["total_answers"])

        if item.get("total_accepted", None) is not None:
            total_accepted = int(item["total_accepted"])

        if item.get("total_unanswered", None) is not None:
            total_unanswered = int(item["total_unanswered"])

        if item.get("total_questions", None) is not None:
            total_questions = int(item["total_questions"])

    adder = DBModelAdder()
    adder.start()
    site_info = SiteInfo(
         site_id,
         total_users,
         total_badges,
         total_votes,
         total_comments,
         total_answers,
         total_accepted,
         total_unanswered,
         total_questions)
    adder.add(site_info)
    adder.done()


def load_answer(site_api_name, answer_id):
    params = {
        "key": STACKEXCHANGE_CLIENT_KEY,
        "site": site_api_name,
        "preview": "false",
        "order": "desc",
        "sort": "creation"
    }
    url = SE_ANSWER_ENDPOINT.replace("{ids}", str(answer_id))
    r = requests.get(url, data=params)
    try:
        data = json.loads(r.text)
    except:
        print r.text
        return None, None

    if data.get("items", None) is None:
        print "Cannot find 'items' prop. %s" % str(data)
        return None, None

    item = data["items"][0]
    if item.get("question_id", None) is not None:
        question_id = int(item["question_id"])
    if item.get("is_accepted", None) is not None:
        is_accepted = bool(item["is_accepted"])

    return question_id, is_accepted


def load_question(site_api_name, question_id):
    params = {
        "key": STACKEXCHANGE_CLIENT_KEY,
        "site": site_api_name,
        "preview": "false",
        "order": "desc",
        "sort": "creation"
    }
    url = SE_QUESTION_ENDPOINT.replace("{ids}", str(question_id))
    r = requests.get(url, data=params)
    try:
        data = json.loads(r.text)
    except:
        print r.text
        return None, None, None, None

    if data.get("items", None) is None:
        print "Cannot find 'items' prop. %s" % str(data)
        return None, None, None, None

    item = data["items"][0]
    if item.get("tags", None) is not None:
        tags = " ".join(item["tags"])

    if item.get("view_count", None) is not None:
        view_count = int(item["view_count"])

    if item.get("answer_count", None) is not None:
        answer_count = int(item["answer_count"])

    if item.get("is_answered", None) is not None:
        is_answered = bool(item["is_answered"])

    return tags, view_count, answer_count, is_answered

def error_handler(data):
    if data.get("error_message", None) is not None:
        error_message = data["error_message"]
    else:
        error_message = str(data)

    if data.get("error_id", None) is not None:
        error_id = int(data["error_id"])
        if error_id == 502:
            time_to_wait = [int(s) for s in error_message.split() if s.isdigit()]
            if len(time_to_wait) > 0:
                time_to_wait = [0]
            else:
                time_to_wait = 10 # almost a random number, it might be needed to change in the future.

            print "Error: %s, msg: %s. Start waiting %s" % (str(error_id), error_message, str(time_to_wait))
            time.sleep(time_to_wait)
            return True

    return False

def load_posts(site_id, site_api_name, since_date):
    current_page = 1
    has_more = True

    while has_more:
        params = {
            "key": STACKEXCHANGE_CLIENT_KEY,
            "site": site_api_name,
            "preview": "false",
            "order": "desc",
            "sort": "creation",
            "page": current_page,
            "filter": SE_POST_FILTER,
            "fromdate": int(time.mktime(since_date.timetuple()))
        }
        r = requests.get(SE_POST_ENDPOINT, data=params)
        try:
            data = json.loads(r.text)
        except:
            return jsonify(**{
                "error": r.text
            })

        if data.get("items", None) is None:
            if not error_handler(data):
                continue
            return "Cannot find 'items' prop. %s" % str(data)

        adder = DBModelAdder()
        adder.start()
        posts = list()

        for item in data["items"]:
            try:
                post_id = int(item["post_id"])
                creation_date = datetime.utcfromtimestamp(
                    int(item["creation_date"])
                )
                score = int(item["score"])
                down_vote_count = int(item["down_vote_count"])
                up_vote_count = int(item["up_vote_count"])
                owner_id = int(item["owner"]['user_id'])
                post_type = item["post_type"]

                if post_type == "question":
                    tags, view_count, answer_count, is_answered = load_question(site_api_name, post_id)
                else: #post_type == "answer"
                    question_id, is_accepted = load_answer(site_api_name, post_id)


                if Post.is_exist(adder, site_id, post_id):
                    pass
                else:
                    if post_type == "question":
                        post = Post.question(
                            site_id,
                            post_id,
                            creation_date,
                            score,
                            down_vote_count,
                            up_vote_count,
                            view_count,
                            answer_count,
                            is_answered,
                            tags,
                            owner_id
                        )
                    else:
                        post = Post.answer(
                            site_id,
                            post_id,
                            question_id,
                            creation_date,
                            score,
                            down_vote_count,
                            up_vote_count,
                            owner_id,
                            is_accepted
                        )
                    posts.append(post)
                    print "Added (%s) %s, %s" % (str(site_id), str(post_id), post_type)
            except:
                print "Something went wrong"
                print sys.exc_info()[0]
        has_more = bool(data['has_more']) if data.get("has_more", None) is not None else False
        current_page += 1

        if len(posts) > 0:
            adder.add_all(posts)

        adder.done()

    return None


def load_sites(filename):
    adder = DBModelAdder()
    adder.start()

    with open(filename) as json_file:
        data = json.load(json_file)
        for item in data["sites"]:
            name    = item["name"]
            url     = item["url"]
            meta    = item["meta"]
            chat    = item["chat"]
            api_name= item["api_name"]
            launch_date = datetime.utcfromtimestamp(
                int(item["launch_date"])
            )

            if Site.is_exist(adder, api_name):
                continue

            site = Site(name, url, meta, chat, api_name, launch_date)
            adder.add(site)
    adder.done()

def load_activities(filename):
    adder = DBModelAdder()
    adder.start()
    activities = list()
    with open(filename) as json_file:
        data = json.load(json_file)
        for item in data["activities"]:
            activity_type   = int(item["activity_type"])
            site_api_name   = item["site_api_name"]
            tab_name        = item["tab_name"]
            title           = item["title"]
            description     = item["description"]
            meta_post_url   = item["meta_post_url"]
            chat_url        = item["chat_url"]

            site = Site.by_api_name(site_api_name)

            if Activity.is_exist(adder, site.id, activity_type):
                print "Activity (%s;%s) found" % (str(activity_type), site_api_name)
                continue

            activities.append(Activity(site.id,
                            title,
                            description,
                            activity_type,
                            meta_post_url,
                            chat_url,
                            tab_name))
            print "Activity (%s;%s) added" % (str(activity_type), site_api_name)

    adder.add_all(activities)
    adder.done()


def load_site_posts(start_date=None):
    sites = Site.all()
    for site in sites:
        last = Post.last(site.id)
        if last is not None:
            print "%s, %s, %s" % (str(site.id), str(last.site_id), str(last.post_id))
            start_date = last.creation_date
        else:
            print "Using predefined start date"

        print "Start loading %s, since %s" % (str(site), str(start_date))
        result = load_posts(site.id, site.api_name, start_date)
        if result is not None:
            print result