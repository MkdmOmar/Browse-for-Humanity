from flask import Flask, redirect, url_for, render_template, request, session, flash
import os, re
from functools import wraps

emailRegexp = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY = os.urandom(24),  # Secret key for app session
    UPLOAD_FOLDER = './uploads',
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
@login_required
def accept():
    if request.method == 'POST':
        typedCode = request.form['typedCode']

        print request.files
        print("here")
        # print request.form['typedCode']
        # print("accepted")
        # print request.form
        # for element in request.form:
        #     print element
        # print("")
        # print "!!!!!!",request.form[""]
        # print request.form['u']
        # tasksFile = request.form['tasksFile']
        # print request.form['codeFile']
        # print request.form['tasksFile']
        for f in request.files:
            obj = request.files[f]
            if obj.filename == '':
                continue
            if f:
                #filename = obj.filename
                filename = "testUser.txt"
                obj.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # if 'file' not in request.files:
        #     #flash('No file part')
        #     return redirect(request.url)
        # file = request.files['tasksFile']
        # if file.filename == '':
        #     #flash('No seleted file')
        #     return redirect(request.url)
        # if file:
        #     print("saving")
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('createJob'))


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Logout of session
@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    flash("You were just logged out!")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
