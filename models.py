import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, ColumnDefault
from meta import app as application, db, db_session
from sqlalchemy import and_, or_, desc, asc, bindparam, text, Interval
from sqlalchemy.sql import func, case, select, update, literal_column, column, join

class DBModelAdder:

    def __init__(self):
        self.session = None

    def start(self):
        self.session = db_session()

    def done(self):
        self.session.commit()
        self.session.close()

    def execute(self, stmnt):
        self.session.execute(stmnt)

    def add(self, inst):
        self.session.add(inst)

    def add_all(self, insts):
        self.session.add_all(insts)

class User(db.Model):
    __tablename__ = 'user'

    id          = db.Column(db.Integer, primary_key=True)
    account_id  = db.Column(db.Integer, unique=True)
    user_id     = db.Column(db.Integer)
    username    = db.Column(db.String(100))
    role        = db.Column(db.String(30))
    is_banned   = db.Column(db.Boolean, default=False)
    end_ban_date= db.Column(db.DateTime, nullable=True)
    reputation  = db.Column(db.Integer)
    profile_image = db.Column(db.String(200))
    profile_link= db.Column(db.String(200))
    creation_date= db.Column(db.DateTime, nullable=False)

    def __init__(self, account_id, user_id, username, reputation, profile_image, profile_link, role="user", is_banned=False):
        self.creation_date = datetime.datetime.now()
        self.account_id = account_id
        self.user_id    = user_id
        self.username   = username
        self.reputation = reputation
        self.profile_image = profile_image
        self.profile_link = profile_link
        self.role       = role
        self.is_banned  = is_banned

    def __repr__(self):
        return '<User %r>' % str(self.id)

    @staticmethod
    def is_exist_with_account_id(adder, account_id):
        return True if adder.session.query(func.count(User.id)).filter_by(account_id=account_id).scalar() > 0 else False

    @staticmethod
    def by_account_id(account_id):
        session = db_session()
        query = session.query(User).filter_by(account_id=account_id).order_by(desc(User.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def by_id(user_id):
        session = db_session()
        query = session.query(User).filter_by(id=user_id).order_by(desc(User.creation_date))
        result = query.first()
        session.close()
        return result

class Site(db.Model):
    __tablename__ = 'site'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100))
    url         = db.Column(db.String(100))
    meta        = db.Column(db.String(100))
    chat        = db.Column(db.String(100))
    api_name    = db.Column(db.String(100), unique=True)
    launch_date = db.Column(db.DateTime, nullable=False)
    creation_date= db.Column(db.DateTime, nullable=False)
    language    = db.Column(db.String(100), unique=True)

    def __init__(self, name, url, meta, chat, api_name, launch_date, language):
        self.creation_date = datetime.datetime.now()
        self.name   = name
        self.url    = url
        self.meta   = meta
        self.chat   = chat
        self.api_name = api_name
        self.launch_date = launch_date
        self.language = language

    @staticmethod
    def is_exist(adder, api_name):
        return True if adder.session.query(func.count(Site.id)).filter_by(api_name=api_name).scalar() > 0 else False

    @staticmethod
    def by_language(language):
        session = db_session()
        query = session.query(Site).filter_by(language=language)
        result = query.first()
        session.close()
        return result

    @staticmethod
    def by_api_name(api_name):
        session = db_session()
        query = session.query(Site).filter_by(api_name=api_name)
        result = query.first()
        session.close()
        return result

    @staticmethod
    def all():
        return Site.query.all()

    def __repr__(self):
        return '<Site %r>' % str(self.id)

class SiteInfo(db.Model):
    __tablename__ = 'site_info'

    id      = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, ForeignKey('site.id'))
    date    = db.Column(db.DateTime, nullable=False)

    total_users     = db.Column(db.Integer)
    total_badges    = db.Column(db.Integer)
    total_votes     = db.Column(db.Integer)
    total_comments  = db.Column(db.Integer)
    total_answers   = db.Column(db.Integer)
    total_accepted  = db.Column(db.Integer)
    total_unanswered= db.Column(db.Integer)
    total_questions = db.Column(db.Integer)

    def __init__(self, site_id, total_users, total_badges, total_votes, total_comments, total_answers, total_accepted, total_unanswered, total_questions):
        self.site_id = site_id
        self.date = datetime.datetime.now()

        self.total_users    = total_users
        self.total_badges   = total_badges
        self.total_votes    = total_votes
        self.total_comments = total_comments
        self.total_answers  = total_answers
        self.total_accepted = total_accepted
        self.total_unanswered = total_unanswered
        self.total_questions  = total_questions

    def __repr__(self):
        return '<SiteInfo %r>' % str(self.id)

class Post(db.Model):
    __tablename__       = 'post'
    post_type_question  = 1
    post_type_answer    = 2

    id          = db.Column(db.Integer, primary_key=True)
    site_id     = db.Column(db.Integer, ForeignKey('site.id'))
    post_id     = db.Column(db.Integer)
    creation_date= db.Column(db.DateTime, nullable=False)
    post_type   = db.Column(db.Integer)
    owner_id    = db.Column(db.Integer)
    score       = db.Column(db.Integer)
    down_vote_count= db.Column(db.Integer)
    up_vote_count= db.Column(db.Integer)

    view_count  = db.Column(db.Integer)
    answer_count= db.Column(db.Integer)
    is_answered = db.Column(db.Boolean, default=False)
    tags        = db.Column(db.String(500))
    is_accepted = db.Column(db.Boolean, default=False)
    parent_id   = db.Column(db.Integer)

    def __init__(self, site_id, post_id, post_type, creation_date, owner_id, score, down_vote_count, up_vote_count):
        self.site_id    = site_id
        self.post_id    = post_id
        self.post_type  = post_type
        self.creation_date= creation_date
        self.owner_id   = owner_id
        self.score      = score
        self.down_vote_count = down_vote_count
        self.up_vote_count = up_vote_count

    @staticmethod
    def question(site_id, question_id, creation_date, score, down_vote_count, up_vote_count, view_count, answer_count, is_answered, tags, owner_id):
        q = Post(site_id,
                 question_id,
                 Post.post_type_question,
                 creation_date,
                 owner_id,
                 score,
                 down_vote_count,
                 up_vote_count)

        q.view_count   = view_count
        q.answer_count = answer_count
        q.is_answered  = is_answered
        q.tags         = tags

        return q

    @staticmethod
    def answer(site_id, answer_id, question_id, creation_date, score, down_vote_count, up_vote_count, owner_id, is_accepted):
        a = Post(site_id,
                 answer_id,
                 Post.post_type_answer,
                 creation_date,
                 owner_id,
                 score,
                 down_vote_count,
                 up_vote_count)

        a.is_accepted= is_accepted
        a.parent_id  = question_id

        return a

    @staticmethod
    def last(site_id):
        session = db_session()
        query = session.query(Post).filter_by(site_id=site_id).order_by(desc(Post.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def is_exist(adder, site_id, post_id):
        return True if adder.session.query(func.count(Post.id)).filter_by(site_id=site_id).filter_by(post_id=post_id).scalar() > 0 else False

    def __repr__(self):
        return '<Post %r>' % str(self.id)

class Activity(db.Model):
    __tablename__       = 'activity'

    activity_type_interesting   = 1
    activity_type_needed        = 2
    activity_type_creative      = 3

    id      = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, ForeignKey('site.id'))
    title   = db.Column(db.String)
    description     = db.Column(db.String)
    creation_date   = db.Column(db.DateTime, nullable=False)
    activity_type   = db.Column(db.Integer)
    meta_post_url   = db.Column(db.String)
    meta_post_title = db.Column(db.String)
    chat_url        = db.Column(db.String)
    chat_name       = db.Column(db.String)

    tab_name    = db.Column(db.String)

    def __init__(self, site_id, title, description, activity_type, meta_post_url, meta_post_title, chat_url, chat_name, tab_name):
        self.creation_date = datetime.datetime.now()
        self.site_id = site_id
        self.title = title
        self.description = description
        self.activity_type = activity_type
        self.meta_post_url = meta_post_url
        self.meta_post_title = meta_post_title
        self.chat_url = chat_url
        self.chat_name = chat_name
        self.tab_name = tab_name

    @staticmethod
    def is_exist(adder, site_id, activity_type):
        return True if adder.session.query(func.count(Activity.id)).filter_by(site_id=site_id).filter_by(activity_type=activity_type).scalar() > 0 else False

    @staticmethod
    def by_site_id_and_activity_type(site_id, activity_type):
        session = db_session()
        query = session.query(Activity).filter_by(site_id=site_id, activity_type=activity_type).order_by(asc(Activity.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def by_id(activity_id):
        session = db_session()
        query = session.query(Activity).filter_by(id=activity_id).order_by(asc(Activity.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def all(site_id):
        session = db_session()
        query = session.query(Activity).filter_by(site_id=site_id).order_by(asc(Activity.creation_date))
        result = query.all()
        session.close()
        return result

    def __repr__(self):
        return '<Activity %r>' % str(self.id)


class Activist(db.Model):
    __tablename__       = 'activist'

    role_coordinator = 1
    role_attendee = 2

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, ForeignKey('user.id'))
    activity_id = db.Column(db.Integer, ForeignKey('activity.id'), nullable=True)
    event_id    = db.Column(db.Integer, ForeignKey('event.id'), nullable=True)
    role        = db.Column(db.Integer)
    creation_date= db.Column(db.DateTime, nullable=False)
    canceled    = db.Column(db.Boolean, default=False)
    updated_date= db.Column(db.DateTime, nullable=True)

    def __init__(self, user_id, activity_id, event_id, role):
        self.creation_date  = datetime.datetime.now()
        self.user_id        = user_id
        self.activity_id    = activity_id
        self.event_id       = event_id
        self.role           = role

    def __repr__(self):
        return '<activist %r>' % str(self.id)

    @staticmethod
    def coordinator(user_id, activity_id):
        return Activist(user_id, activity_id, None, Activist.role_coordinator)

    @staticmethod
    def attendee(user_id, event_id):
        return Activist(user_id, None, event_id, Activist.role_coordinator)

    @staticmethod
    def coordinators(activity_id):
        session = db_session()
        query = session.query(User).join(Activist).filter_by(activity_id=activity_id,
                                                             role=Activist.role_coordinator,
                                                             canceled=False).order_by(asc(Activist.creation_date))
        result = query.all()
        session.close()
        return result

    @staticmethod
    def attendees(event_id):
        session = db_session()
        query = session.query(User).join(Activist).filter_by(event_id=event_id,
                                                             role=Activist.role_attendee,
                                                             canceled=False).order_by(asc(Activist.creation_date))
        result = query.all()
        session.close()
        return result

    @staticmethod
    def is_attendee(user_id, event_id):
        session = db_session()
        result = session.query(func.count(Activist.id)).filter_by(user_id=user_id,
                                                                  event_id=event_id,
                                                                  role=Activist.role_attendee,
                                                                  canceled=False).scalar()
        session.close()
        return True if result > 0 else False

    @staticmethod
    def user_attend_times(user_id, site_id):
        session = db_session()
        result = session.query(func.count(Activist.id)).join(Event).filter(
            Activist.user_id == user_id, Activist.role == Activist.role_attendee, Activist.canceled==False, Event.site_id == site_id).scalar()
        session.close()
        return result

    @staticmethod
    def user_coordinate_times(user_id, site_id):
        session = db_session()
        result = session.query(func.count(Activist.id)).join(Activity).filter(
            Activist.user_id == user_id,
            Activist.role == Activist.role_coordinator,
            Activist.canceled == False,
            Activity.site_id == site_id).distinct().scalar()
        session.close()
        return result

    @staticmethod
    def is_coordinator(user_id):
        session = db_session()
        result = session.query(func.count(Activist.id)).filter_by(user_id=user_id, role=Activist.role_coordinator).scalar()
        session.close()
        return True if result > 0 else False

    @staticmethod
    def by_user_and_event(user_id, event_id):
        session = db_session()
        query = session.query(Activist).filter_by(event_id=event_id, user_id=user_id, role=Activist.role_attendee).order_by(asc(Activist.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def is_exist(adder, activity_id, user_id):
        return True if adder.session.query(func.count(Activist.id)).filter_by(activity_id=activity_id, user_id=user_id).scalar() > 0 else False


class Action(db.Model):
    __tablename__       = 'action'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, ForeignKey('user.id'))
    activity_id = db.Column(db.Integer, ForeignKey('activity.id'))
    creation_date= db.Column(db.DateTime, nullable=False)

    post_id     = db.Column(db.Integer, ForeignKey('post.id'), nullable=True)
    link        = db.Column(db.String)

    def __init__(self, user_id, activity_id, post_id, link):
        self.user_id    = user_id
        self.activity_id= activity_id
        self.post_id    = post_id
        self.link       = link
        self.creation_date = datetime.datetime.now()

    def __repr__(self):
        return '<Action %r>' % str(self.id)

    @staticmethod
    def all_for_activity(activity_id):
        session = db_session()
        query = session.query(Action).filter_by(activity_id=activity_id).order_by(asc(Action.creation_date))
        result = query.all()
        session.close()
        return result

    @staticmethod
    def activists(activity_id):
        session = db_session()
        query = session.query(User).join(Action).filter(Action.activity_id==activity_id).distinct()
        result = query.all()
        session.close()
        return result

    @staticmethod
    def user_act_times(user_id, site_id):
        session = db_session()
        result = session.query(func.count(Action.id)).join(Activity).filter(
            Action.user_id == user_id, Activity.site_id == site_id).scalar()
        session.close()
        return result

    @staticmethod
    def last_by_user(user_id):
        session = db_session()
        query = session.query(Action).filter_by(user_id=user_id).order_by(desc(Action.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def by_id(action_id):
        session = db_session()
        query = session.query(Action).filter_by(id=action_id).order_by(asc(Action.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def is_exist(adder, activity_id, link):
        return True if adder.session.query(func.count(Action.id)).filter_by(activity_id=activity_id).filter_by(link=link).scalar() > 0 else False


class Verification(db.Model):
    __tablename__       = 'verification'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, ForeignKey('user.id'))
    action_id   = db.Column(db.Integer, ForeignKey('action.id'))
    creation_date= db.Column(db.DateTime, nullable=False)
    is_valid    = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, action_id, is_valid):
        self.user_id = user_id
        self.action_id = action_id
        self.is_valid = is_valid
        self.creation_date = datetime.datetime.now()

    @staticmethod
    def by_user_and_action(user_id, action_id):
        session = db_session()
        query = session.query(Verification).filter_by(user_id=user_id, action_id=action_id).order_by(asc(Verification.creation_date))
        result = query.first()
        session.close()
        return result


class Event(db.Model):
    __tablename__       = 'event'

    event_type_meetup   = 1
    event_type_webcast  = 2
    event_type_makeathon= 3

    id          = db.Column(db.Integer, primary_key=True)
    created_by  = db.Column(db.Integer, ForeignKey('user.id'))
    site_id     = db.Column(db.Integer, ForeignKey('site.id'))
    creation_date= db.Column(db.DateTime, nullable=False)
    date        = db.Column(db.DateTime, nullable=False)
    title       = db.Column(db.String)
    description = db.Column(db.String)
    location    = db.Column(db.String)
    meta_link   = db.Column(db.String)
    meta_post_id= db.Column(db.Integer)
    chat_link   = db.Column(db.String)
    event_type  = db.Column(db.Integer)


    is_valid    = db.Column(db.Boolean, default=True, nullable=True)
    validated_by= db.Column(db.Integer, ForeignKey('user.id'), nullable=True)

    def __init__(self, event_type, created_by, site_id, date, title, description, location, meta_link, meta_post_id, chat_link):
        self.creation_date = datetime.datetime.now()
        self.event_type = event_type
        self.created_by = created_by
        self.site_id = site_id
        self.date = date
        self.title = title
        self.description = description
        self.location = location
        self.meta_link = meta_link
        self.meta_post_id = meta_post_id
        self.chat_link = chat_link

    @staticmethod
    def by_meta_post_id(meta_post_id, site_id):
        session = db_session()
        query = session.query(Event).filter(
            Event.meta_post_id == meta_post_id, Event.site_id == site_id).order_by(asc(Event.creation_date))
        result = query.first()
        session.close()
        return result

    @staticmethod
    def by_id(event_id):
        session = db_session()
        query = session.query(Event).filter_by(id=event_id).order_by(asc(Event.creation_date))
        result = query.first()
        session.close()
        return result