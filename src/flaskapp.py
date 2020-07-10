from flask import Flask, session, redirect, url_for, request, render_template, flash
from dotenv import load_dotenv
from backend import Backend

app = Flask(__name__)

app.secret_key = 'uaiYSaYISUS41567YDabhY&WQT23YTEEiubz'

#subtitle for template
sub = "Pulumafia (H) | Stormscale-EU"

backend = Backend()

@app.route('/')
def index():
    roster = backend.getView()
    logs = backend.getLogs()
    user = None
    if 'username' in session:
        user = session['username']
    return render_template('index.html', sub=sub, user=user, data=roster, logs=logs)

@app.route('/blog')
@app.route('/blog/<id>')
def blog():
    posts = backend.getBlog()
    user = None
    if 'username' in session:
        user = session['username']
    return render_template('blog.html', sub=sub,user=user, posts=posts)

@app.route('/admin')
def admin():
    user = None
    if 'username' in session:
        user = session['username']
        return render_template('admin.html', sub=sub, user=user)
    else:
        flash("Please login!")
        return redirect(url_for('index'))
    

@app.route('/post', methods=["POST"])
def postblog():
    print(request.form)
    r=backend.post(request.form['title'], request.form['post'])
    if r:
        flash("Success!")
    else:
        flash("Failure!")
        
    return redirect(url_for('admin'))

@app.route('/login', methods=['POST'])
def login():
    username_exists = False
    password_matches = False

    # check credentials against DB
    given_username = request.form['username']
    given_pwd = request.form['password']

    username_exists, password_matches = backend.login(given_username, given_pwd)

    if username_exists:
        print("username exists")
        if password_matches:
            print("password matches")
            session['username'] = request.form['username']
        else:
            flash("Incorrect credentials!")
            print("wrong pwd")
    else:
        flash("Incorrect credentials!")
        print("wrong usr")
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(port=1337, debug=True, host="0.0.0.0")