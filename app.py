from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

# Main login page
@app.route("/")
def login():
    print("logged in!")
    return render_template('login.html')

# If login success route to index.html. Else, return to login page.
@app.route('/checkLogin', methods = ['POST', 'GET'])
def checkLogin():
    print("checkLogin")
    if request.method == 'POST' and request.form['username'] == 'admin' and request.form['password'] == 'password':
        return render_template('index.html')
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
