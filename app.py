from flask import Flask, redirect, url_for, render_template, request, session, flash
import os, re
from functools import wraps
import os
import json
from werkzeug.utils import secure_filename
import threading
import six
from threading import Timer

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

UPLOAD_FOLDER = './uploads'
JOB_PATH = './results'

job_id_lock = threading.Lock()
last_job_id = 0

jobs = {}

class Job:
   def __init__(self, username, task_file, code, job_id, max_time=1000):
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
     job_info  = jobs[job_id]
     result = lzw_decode(result)
     #wait on semaphore
     with job_info.result_lock:
         print task_id,  " In scheduled tasks?"
         if task_id in job_info.scheduled_tasks:
             print "yes ", result
             json.dump((job_info.scheduled_tasks[task_id], result), job_info.out_file)
             job_info.out_file.write('\n')
             del job_info.scheduled_tasks[task_id];
             if (job_info.is_done()):
                 print job_id, " done!"
                 job_info.out_file.close()
     #release semaphore

@app.route('/get_job')
def get_job():
     for job_id, job in six.iteritems(jobs):
         if len(job.tasks_to_do) > 0:
             task_id, params = job.tasks_to_do.popitem()
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
            session['userEmail'] = request.form['email']
            print(session['userEmail'])
            return redirect(url_for('createJob'))
        else:
            return render_template('login.html', error = 'Invalid credentials. Please try again!')


# Create a job to be run on workers
@app.route("/createJob")
@login_required
def createJob():
    return render_template('createJob.html', email = session['userEmail'])


@app.route("/accept", methods = ['POST', 'GET'])
@login_required
def accept():
    if request.method == 'POST':
        code = ''
        email = request.form['email']

        if request.files['fileCode'] and request.files['fileCode'] != '':
            file = request.files['fileCode']
            filename = "code" + email + ".txt"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("NOT IMPLEMENTED")
            return redirect(url_for('createJob'))
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


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Logout of session
@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('userEmail', None)
    flash("You were just logged out!")
    return redirect(url_for('login'))


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, threaded=True)
