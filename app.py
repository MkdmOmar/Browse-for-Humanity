from flask import Flask, redirect, url_for, render_template, request, session, flash
import os
from functools import wraps

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY = os.urandom(24)  # Secret key for app session
)


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session: # If logged_in, proceed as intended
            return f(*args, **kwargs)
        else: # Else, redirect to login page
            flash('You need to login first!')
            return redirect(url_for('login'))
    return wrap

# Login page
@app.route("/")
def login():
    return render_template('login.html', error = None)

# If login success route to index.html. Else, return to login page with error message.
@app.route('/checkLogin', methods = ['POST', 'GET'])
def checkLogin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            flash("You were successfully logged in!")
            return redirect(url_for('createJob'))
        else:
            return render_template('login.html', error = 'Invalid credentials. Please try again!')

#
@app.route("/createJob")
@login_required
def createJob():
    return render_template('createJob.html')

@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    flash("You were just logged out!")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
