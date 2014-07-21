from google.appengine.ext import ndb
from flask import Flask, request, session, redirect, url_for, abort, \

import time
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

# Set up schemes
class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    following = ndb.ListProperty(ndb.Key)
    start_date = ndb.DateTimeProperty(auto_now_add=True)
    messages = ndb.StructuredProperty(Message, repeated=True)
    
class Message(ndb.Model):
    author = ndb.KeyProperty()
    text = ndb.TextProperty(required=True)
    pub_date = ndb.DateTimeProperty(auto_now_add=True)


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
     #    g.user = query_db('select * from user where user_id = ?',
     #                      [session['user_id']], one=True)
        g.user = User.get_by_id(session['user_id'])

@app.route('/')
def timeline():
	"""Shows a users timeline or if no user is logged in it will
	redirect to the public timeline.  This timeline shows the user's
	messages as well as all the messages of followed users.
	"""
	if not g.user:
	    return redirect(url_for('public_timeline'))
	
	id = session['use_id']
	following_ids = User.get_by_id(id)['following']
	ids = following_ids.append(id)
	_l = []
	for current_id in ids:
		current_entity = User.get_by_id(current_id)
		for current_message in current_entity['messages']:
			_d = {}
			_d['username'] = current_entity['username']
			_d['text'] = current_message['text']
			_d['pub_date'] = current_message['pub_date']
			_l.append(_d)
	_l = sorted(_l, key = lambda x:x['pub_date'], reversed = True) 
	_l = _l[0:30] 
	#  return render_template('timeline.html', messages=query_db('''
	#  select message.*, user.* from message, user
	#  where message.author_id = user.user_id and (
	#   user.user_id = ? or
	#   user.user_id in (select whom_id from follower
	#                           where who_id = ?))
	#  order by message.pub_date desc limit ?''',
	# [session['user_id'], session['user_id'], PER_PAGE]))
	return render_template('timeline.html', messages = _l)
        
@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
    	new_message = Message(author = session['user_id'], text = request.form['text'])
		new_message.put()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = User.query(username == request.form['username']).get()
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.key.id()
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)

def get_user_id(u):
	a = User.query(username==u).fetch()
	if len(a) > 0:
		return True
	return False

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id:
            error = 'The username is already taken'
        else:
            new_user = User(username = request.form['username'], email = request.form['email'], \
            	pw_hash = generate_password_hash(request.form['password']))
            new_user.put()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url


if __name__ == '__main__':
    init_db()
    app.run()
