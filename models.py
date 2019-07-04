import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, ColumnDefault
from meta import app as application, db, db_session
from sqlalchemy import and_, or_, desc, asc, bindparam, text, Interval
from sqlalchemy.sql import func, select, update, literal_column, column, join

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
    is_banned   = db.Column(db.Boolean)
    end_ban_date= db.Column(db.DateTime, nullable=True)
    reputation  = db.Column(db.Integer)
    profile_image = db.Column(db.String(200))
    profile_link= db.Column(db.String(200))

    def __init__(self, account_id, user_id, username, reputation, profile_image, profile_link, role="user", is_banned=False):
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

    def __init__(self, name, url, meta, chat, api_name, launch_date):
        self.creation_date = datetime.datetime.now()
        self.name   = name
        self.url    = url
        self.meta   = meta
        self.chat   = chat
        self.api_name = api_name
        self.launch_date = launch_date

    @staticmethod
    def is_exist(adder, api_name):
        return True if adder.session.query(func.count(Site.id)).filter_by(api_name=api_name).scalar() > 0 else False

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

    activity_type_self_answered = 1
    activity_type_translation   = 2
    activity_type_interesting   = 3

    id      = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, ForeignKey('site.id'))
    title   = db.Column(db.String)
    description = db.Column(db.String)
    creation_date   = db.Column(db.DateTime, nullable=False)
    activity_type   = db.Column(db.Integer)
    meta_post_url   = db.Column(db.String)
    chat_url    = db.Column(db.String)
    tab_name    = db.Column(db.String)

    def __init__(self, site_id, title, description, activity_type, meta_post_url, chat_url, tab_name):
        self.creation_date = datetime.datetime.now()
        self.site_id = site_id
        self.title = title
        self.description = description
        self.activity_type = activity_type
        self.meta_post_url = meta_post_url
        self.chat_url = chat_url
        self.tab_name = tab_name

    @staticmethod
    def is_exist(adder, site_id, activity_type):
        return True if adder.session.query(func.count(Activity.id)).filter_by(site_id=site_id).filter_by(activity_type=activity_type).scalar() > 0 else False

    def __repr__(self):
        return '<Activity %r>' % str(self.id)


class Activist(db.Model):
    __tablename__       = 'activist'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    activity_id = db.Column(db.Integer, ForeignKey('activity.id'))
    role        = db.Column(db.Integer)

class Action(db.Model):
    __tablename__       = 'action'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, ForeignKey('user.id'))
    activity_id = db.Column(db.Integer, ForeignKey('activity.id'))
    creaton_date= db.Column(db.DateTime, nullable=False)

    post_id     = db.Column(db.Integer, ForeignKey('post.id'))
    link        = db.Column(db.String)

    valid       = db.Column(db.Boolean, default=False)
    verified    = db.Column(db.Boolean, default=False)
    verified_date= db.Column(db.DateTime, nullable=False)

class Verification(db.Model):
    __tablename__       = 'verification'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, ForeignKey('user.id'))
    action_id   = db.Column(db.Integer, ForeignKey('action.id'))
    creation_date= db.Column(db.DateTime, nullable=False)
    is_valid    = db.Column(db.DateTime, nullable=False)