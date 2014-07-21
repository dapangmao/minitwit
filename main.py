
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash
from google.appengine.ext import ndb

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

# Set up schemes
class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    following = ndb.KeyProperty(repeated=True)
    start_date = ndb.DateTimeProperty(auto_now_add=True)
    
class Message(ndb.Model):
    author = ndb.StringProperty()
    text = ndb.TextProperty(required=True)
    pub_date = ndb.DateTimeProperty(auto_now_add=True)
    
def get_user_id(u):
    a = User.query(User.username == u).get()
    if a:
        return a.key.id() 
    else:
        return None


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
        g.user = User.get_by_id(session['user_id'])

@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline. This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    cid = session['user_id']
    f = User.get_by_id(cid).following
    ids = f if isinstance(f, list) else [f]
    ids.append(cid)
    try:
        messages = Message.query(Message.author.IN(ids)).order(-Message.pub_date).fetch(30)
    except:
        messages = []
    return render_template('timeline.html', messages = messages)
    
@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    messages = Message.query().order(-Message.pub_date).fetch(30)
    return render_template('timeline.html', messages = messages)

@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    cid = session['user_id']
    profile_user = User.query(username == username).get()
    pid = profile_user.key.id()
    if profile_user is None:
        abort(404)
    followed = False
    if g.user and pid in User.get_by_id(cid).following:
        followed = True
    return render_template('timeline.html', messages = Message.query(Message.author == pid).order(-Message.pub_date).fetch(30), \
    		followed = followed, \
            profile_user = profile_user)
			
			
@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    cid = session['user_id']
    if not g.user:
        abort(401)
    
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    a = User.get_by_id(cid).following.append(whom_id)
    a.put()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    cid = session['user_id']
    if not g.user:
        abort(401)

    whom_id = get_user_id(username)
    
    if whom_id is None:
        abort(404)

    a = User.get_by_id(cid).following.remove(whom_id)
    a.put()
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
        user = User.query(User.username == request.form['username']).get()
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user.pw_hash,
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = get_user_id(request.form['username'])
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


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
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            a = User(username = request.form['username'], email = request.form['email'], \
            	pw_hash = generate_password_hash(request.form['password']))
            a.put()
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
    app.run()
