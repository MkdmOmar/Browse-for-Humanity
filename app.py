from flask import Flask, redirect, url_for, render_template, request, session, flash
import os, re
from functools import wraps

emailRegexp = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


app = Flask(__name__)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY = os.urandom(24),  # Secret key for app session
    UPLOAD_FOLDER = '/upload',
    SEND_FILE_MAX_AGE_DEFAULT = 0
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
        if emailRegexp.match(request.form['email']) and request.form['password'] == 'password':
            session['logged_in'] = True
            flash(request.form['email'] + ", you were successfully logged in!")
            return redirect(url_for('createJob'))
        else:
            return render_template('login.html', error = 'Invalid credentials. Please try again!')


# Create a job to be run on workers
@app.route("/createJob")
@login_required
def createJob():
    return render_template('createJob.html')



@app.route("/accept", methods = ['POST', 'GET'])
def accept():
    print("here")
    if request.method == 'POST':
        print("accepted")
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No seleted file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


# Logout of session
@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    flash("You were just logged out!")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
