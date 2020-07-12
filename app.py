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

    # TODO needs method, ugly
    updated = ""
    settings = backend.db.getSettings()

    if settings["updated"] == "never":
        updated = "never"
    else:
        updated = time.strftime('%Y-%m-%d', settings["updated"])

    if 'username' in session:
        user = session['username']
    return render_template('index.html', sub=sub, user=user, data=roster, logs=logs, updated=updated)

@app.route('/blog')
@app.route('/blog/<int:id>')
def blog(id=None):
    if id is None:
        posts = backend.getBlog()
        user = None
        if 'username' in session:
            user = session['username']
        return render_template('blog.html', sub=sub,user=user, posts=posts, single=False)
    else:
        post = backend.getSingleBlog(id)
        if 'username' in session:
            user = session['username']
        return render_template('blog.html', sub=sub,user=user, post=post, single=True)


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

@app.route('/update')
def updateIndex():
    status = backend.updateRoster()
    flash("Roster update initiated, please refresh soon!")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
