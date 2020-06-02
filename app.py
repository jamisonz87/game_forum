from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required
from flask_security.forms import RegisterForm
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'somesaltfromtheform'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#######################################################################
# SQLALCHMEY TABLES
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    replies = db.relationship('Reply', backref='user', lazy='dynamic')

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    description = db.Column(db.String(200))
    date_created = db.Column(db.DateTime())
    thread_type = db.Column(db.String(30))

    replies = db.relationship('Reply', backref='thread', lazy='dynamic')

    def last_post_date(self):
        last_replay = Reply.query.filter_by(thread_id=self.id).order_by(Reply.id.desc()).first()

        if last_replay:
            return last_replay.date_created

        return self.date_created

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(200))
    date_created = db.Column(db.DateTime())
##########################################################################

# FORMS AND EXTENSIONS
class ExtendingRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')

class NewThread(FlaskForm):
    title = StringField('title', validators=[InputRequired('Please Enter a Thread Title')])
    description = TextAreaField('description', validators=[InputRequired('Please Enter a Post')])

class NewReply(FlaskForm):
    message = TextAreaField('Message', validators=[InputRequired('Please Enter Reply!!!!')])

###########################################################################

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendingRegisterForm)

@app.route('/')
def index():

    thread_game_count = Thread.query.filter_by(thread_type='games').count()
    thread_board_count = Thread.query.filter_by(thread_type='board').count()
    thread_card_count = Thread.query.filter_by(thread_type='card').count()
    thread_sport_count = Thread.query.filter_by(thread_type='sports').count()

    return render_template('index.html',thread_game_count=thread_game_count, thread_board_count=thread_board_count,thread_card_count=thread_card_count, thread_sport_count=thread_sport_count)

@app.route('/games', methods=['GET', 'POST'])
def games():
    form = NewThread()

    if form.validate_on_submit():
        new_thread = Thread(title=form.title.data, description=form.description.data, date_created=datetime.now(), thread_type='games')
        db.session.add(new_thread)
        db.session.commit()

    threads = Thread.query.filter_by(thread_type='games').all()

    return render_template('games.html', form=form, threads=threads)

@app.route('/games/<thread_id>', methods=['GET','POST'])
def games_thread(thread_id):
    form = NewReply()

    thread = Thread.query.get(int(thread_id))

    if form.validate_on_submit():
        reply = Reply(user_id=current_user.id, message=form.message.data, date_created=datetime.now())
        thread.replies.append(reply)
        db.session.commit()

    replies = Reply.query.filter_by(thread_id=thread_id).all()

    return render_template('game_thread.html', form=form, thread=thread, replies=replies)

@app.route('/card', methods=['GET', 'POST'])
def card():
    form = NewThread()

    if form.validate_on_submit():
        new_thread = Thread(title=form.title.data, description=form.description.data, date_created=datetime.now(), thread_type='card')
        db.session.add(new_thread)
        db.session.commit()

    threads = Thread.query.filter_by(thread_type='card').all()

    return render_template('card.html', form=form, threads=threads)

@app.route('/card/<thread_id>', methods=['GET','POST'])
def card_thread(thread_id):
    form = NewReply()

    thread = Thread.query.get(int(thread_id))

    if form.validate_on_submit():
        reply = Reply(user_id=current_user.id, message=form.message.data, date_created=datetime.now())
        thread.replies.append(reply)
        db.session.commit()

    replies = Reply.query.filter_by(thread_id=thread_id).all()

    return render_template('game_thread.html', form=form, thread=thread, replies=replies)

@app.route('/board', methods=['GET', 'POST'])
def board():
    form = NewThread()

    if form.validate_on_submit():
        new_thread = Thread(title=form.title.data, description=form.description.data, date_created=datetime.now(), thread_type='board')
        db.session.add(new_thread)
        db.session.commit()

    threads = Thread.query.filter_by(thread_type='board').all()

    return render_template('board.html', form=form, threads=threads)

@app.route('/board/<thread_id>', methods=['GET','POST'])
def board_thread(thread_id):
    form = NewReply()

    thread = Thread.query.get(int(thread_id))

    if form.validate_on_submit():
        reply = Reply(user_id=current_user.id, message=form.message.data, date_created=datetime.now())
        thread.replies.append(reply)
        db.session.commit()

    replies = Reply.query.filter_by(thread_id=thread_id).all()

    return render_template('board_thread.html', form=form, thread=thread, replies=replies)

@app.route('/sports', methods=['GET', 'POST'])
def sports():

    form = NewThread()

    if form.validate_on_submit():
        new_thread = Thread(title=form.title.data, description=form.description.data, date_created=datetime.now(), thread_type='sports')
        db.session.add(new_thread)
        db.session.commit()

    threads = Thread.query.filter_by(thread_type='sports').all()

    return render_template('sports.html', form=form, threads=threads)

@app.route('/sports/<thread_id>', methods=['GET','POST'])
def sports_thread(thread_id):
    form = NewReply()

    thread = Thread.query.get(int(thread_id))

    if form.validate_on_submit():
        reply = Reply(user_id=current_user.id, message=form.message.data, date_created=datetime.now())
        thread.replies.append(reply)
        db.session.commit()

    replies = Reply.query.filter_by(thread_id=thread_id).all()

    return render_template('sports_thread.html', form=form, thread=thread, replies=replies)

if __name__ == '__main__':
    app.run(debug=True)