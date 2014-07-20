from google.appengine.ext import ndb
from flask import Flask, request, session, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

class Records(ndb.Model):
    title = ndb.StringProperty(required=True)
    text = ndb.TextProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

@app.route('/')
def show_entries():
    entries = Records.query().order(-Records.date).fetch(20)
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    a = request.form['title']
    b = request.form['text']
    if not a or not b:
        flash("You must enter title and text")
    else:
        entry = Records(title = a, text = b)
        entry.put()
        flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
