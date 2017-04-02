#!usr/bin/python

from flask import Flask, redirect, url_for, render_template, request, session, flash, send_from_directory
import os, re
from functools import wraps
import os, json, threading, six, stripe, time
from werkzeug.utils import secure_filename
from threading import Timer
import logging

#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

# PUBLISHABLE_KEY= "pk_test_6pRNASCoBOKtIshFeQd4XMUh"
# SECRET_KEY=sk_test_BQokikJOvBiI2HlWgH4olfQ2 python app.py

PUBLISHABLE_KEY= "pk_test_6pRNASCoBOKtIshFeQd4XMUh"
SECRET_KEY= "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

stripe_keys = {
  # 'secret_key': os.environ['SECRET_KEY'],
  # 'publishable_key': os.environ['PUBLISHABLE_KEY']

    'secret_key': SECRET_KEY,
    'publishable_key': PUBLISHABLE_KEY
}

stripe.api_key = stripe_keys['secret_key']

customer = ""

emailRegexp = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

ALLOWED_EXTENSIONS = set(['txt'])

linodeHost = "199.74.58.111"
linodePort = 80

debugHost = "localhost"
debugPort = 8000

debug = False

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY = os.urandom(24),  # Secret key for app session
    UPLOAD_FOLDER = './uploads',
    SEND_FILE_MAX_AGE_DEFAULT = 0
)

UPLOAD_FOLDER = './uploads'
JOB_PATH = './results'

dispatch_lock = threading.Lock()
job_id_lock = threading.Lock()
last_job_id = 0

jobs = {}

class Job:
   def __init__(self, username, task_file, code, job_id, max_time=15):
         self.result_lock = threading.Lock()
         self.queue_lock = threading.Lock()

         self.code = code
         self.max_time = max_time
         self.user = username
         self.done = False
         self.tasks_to_do = {}
         self.scheduled_tasks = {}
         self.out_file_name = os.path.join(JOB_PATH, '{}.json'.format(last_job_id))
         self.out_file = open(self.out_file_name, 'wb')
         self.start_time = int(time.time())
         self.end_time = None

         params = []
         with open(task_file, 'rb') as f:
             params = json.load(f)

         for i in xrange(len(params)):
             self.tasks_to_do[i] = params[i]

   def check_task(self, task_id):
      #wait on semaphore
      with self.queue_lock:
          if task_id in self.scheduled_tasks:
              self.tasks_to_do[task_id] = self.scheduled_tasks[task_id]
              del self.scheduled_tasks[task_id]
              print "Task {} returned to the queue...".format(task_id)

   def is_done(self):
      return len(self.scheduled_tasks) + len(self.tasks_to_do) == 0;

def write_result(job_id, task_id, result):
     if job_id in jobs:
         job_info  = jobs[job_id]
         #wait on semaphore
         with job_info.result_lock:
             print "result for taks {} came back!".format(task_id)
             if task_id in job_info.scheduled_tasks:

                 json.dump((job_info.scheduled_tasks[task_id], result), job_info.out_file)
                 job_info.out_file.write('\n')
                 del job_info.scheduled_tasks[task_id];

                 if (job_info.is_done()):
                     job_info.end_time = int(time.time())
                     print "Job {} done in {} secs!".format(job_id, job_info.end_time - job_info.start_time)
                     job_info.out_file.close()
         #release semaphore

@app.route('/get_job')
def get_job():
     with dispatch_lock:
         for job_id, job in six.iteritems(jobs):
             if len(job.tasks_to_do) > 0:
                 task_id, params = job.tasks_to_do.popitem()
                 print "Popped task {}!".format(task_id)
                 job.scheduled_tasks[task_id] = params
                 Timer(job.max_time, job.check_task, kwargs={'task_id': task_id}).start()
                 return json.dumps({"job_id": job_id,
                                    "task_id": task_id,
                                    "params": params,
                                    "code": job.code})

         return 'X_X'

@app.route('/submit_result')
def submit_result():
     job_id = int(request.args.get('job_id'))
     task_id = int(request.args.get('task_id'))
     result  = request.args.get('result')
     write_result(job_id, task_id, result)
     return "Thanks"

#### ANTONY AND OMAR LAND
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session: # If logged_in, proceed as intended
            return f(*args, **kwargs)
        else: # Else, redirect to login page
            flash('You need to login first!')
            return redirect(url_for('login'))
    return wrap

# Landing page
@app.route("/")
def landing():
    return render_template('index.html')

# Login page
@app.route("/login")
def login():
    formURL = ""
    if debug:
        formURL = "http://" + str(debugHost) + ":" + str(debugPort) + "/checkLogin"
    else:
        formURL = "http://" + str(linodeHost) + ":" + str(linodePort) + "/checkLogin"
    return render_template('login.html', error = None, formAddress = formURL, key=stripe_keys['publishable_key'], debug= debug)

# If login success route to index.html. Else, return to login page with error message.
@app.route('/checkLogin', methods = ['POST', 'GET'])
def checkLogin():
    if request.method == 'POST':
        if emailRegexp.match(request.form['email']) and request.form['password'] == 'password':
            amount = 500
            global customer
            if debug == True:
                customer = ""
            else:
                customer = stripe.Customer.create(
                    email= request.form['email'],
                    source=request.form['stripeToken']
                )
            print customer

            session['logged_in'] = True
            flash(request.form['email'] + ", you were successfully logged in!")
            session['userEmail'] = request.form['email']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error = 'Invalid credentials. Please try again!')



# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    print("got to Dashboard!")
    return render_template('dashboard.html')


@app.route('/viewJobs')
@login_required
def viewJobs():
    username = session['userEmail']
    print username
    files = []

    print jobs
    for jobName in jobs:
        job = jobs[jobName]

        timediff = job["end_time"] - job["start_time"]
        # print job.out_file
        if job['user'] == username:
            file = {"username": username,
            # "file": job["out_file"],
            "filename": job["out_file_name"],
            "time" : timediff}
            files.append(file)

    for file in files:
            obj = {
                "filename": file["filename"],
                "time": file["time"]
            }
            flash(obj)
    return render_template('viewJobs.html')

@app.route('/viewJobs/<filename>')
@login_required
def download(filename):

    if (debug == False):
        amount = 500
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )
        print(charge)
    return send_from_directory(JOB_PATH, filename)


# Create a job to be run on workers
@app.route("/createJob")
@login_required
def createJob():
    formURL = ""
    if debug:
        formURL = "http://" + str(debugHost) + ":" + str(debugPort) + "/accept"
    else:
        formURL = "http://" + str(linodeHost) + ":" + str(linodePort) + "/accept"
    return render_template('createJob.html', email = session['userEmail'], formAddress = formURL)


@app.route("/accept", methods = ['POST', 'GET'])
@login_required
def accept():
    if request.method == 'POST':
        code = ''
        email = request.form['email']

        if request.files['fileCode'] and request.files['fileCode'] != '':
            file = request.files['fileCode']
            filename = "code" + email + ".txt"
            full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_file_path)
            with open(full_file_path, 'r') as myfile:
                code = myfile.read()
        elif request.form['typedCode'] and request.form['typedCode'] != '':
            code = request.form['typedCode']
        else:
            flash("No code given")
            return redirect(url_for('createJob'))


        task_file_name = ''
        if request.files['tasksFile'] and request.files['tasksFile'] != '':
            file = request.files['tasksFile']
            task_file_name = "tasks" + email + ".txt"
            task_file_name = os.path.join(app.config['UPLOAD_FOLDER'], task_file_name)
            file.save(task_file_name)
        else:
            flash("No task file")
            return redirect(url_for('createJob'))
        global job_id_lock
        global last_job_id
        with job_id_lock:
            jobs[last_job_id] = Job(email, task_file_name, code, last_job_id)
            last_job_id += 1

    return redirect(url_for('createJob'))



# Logout of session
@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('userEmail', None)
    flash("You were just logged out!")
    return redirect(url_for('landing'))


if __name__ == "__main__":
    if debug:
        app.run(host='0.0.0.0', port = debugPort, threaded=True)
    else:
        app.run(host='0.0.0.0', port = 80, threaded=True)
