from flask import Flask, session, redirect, url_for, request, render_template, flash
from dotenv import load_dotenv
from backend import Backend
import time

app = Flask(__name__)

app.secret_key = 'uaiYSaYISUS41567YDabhY&WQT23YTEEiubz'

#subtitle for template
sub = "Pulumafia (H) | Stormscale-EU"

backend = Backend()

@app.route('/')
def index():
    sidebar = backend.getSideBar()
    roster = backend.getView()
    logs = backend.getLogs()
    user = None

    # get timestamp for last update
    updatetime = backend.getUpdateTimestamp()
    updated = "never"

    # if db has no update time, just return never
    if updatetime == "never":
        pass
    # if it has timestamp, calculate delta to current time
    else:
        timenow = time.time()
        delta = timenow-updatetime
        updated = time.strftime("%H hours, %M minutes, %S seconds ago", time.gmtime(delta))

    if 'username' in session:
        user = session['username']
    return render_template('index.html', sub=sub, user=user, data=roster, logs=logs, updated=updated, sidebar=sidebar)

@app.route('/blog')
@app.route('/blog/<int:id>')
def blog(id=None):
    sidebar = backend.getSideBar()
    if id is None:
        posts = backend.getBlog()
        user = None
        if 'username' in session:
            user = session['username']
        return render_template('blog.html', sub=sub,user=user, posts=posts, single=False, sidebar=sidebar)
    else:
        post = backend.getSingleBlog(id)
        if 'username' in session:
            user = session['username']
        return render_template('blog.html', sub=sub,user=user, post=post, single=True, sidebar=sidebar)


@app.route('/admin')
def admin():

    players = backend.getView()
    sidebar = backend.getSideBar()

    user = None
    if 'username' in session:
        user = session['username']
        return render_template('admin.html', sub=sub, user=user, players=players, sidebar=sidebar)
    else:
        flash("Please login!")
        return redirect(url_for('index'))
    

@app.route('/post', methods=["POST"])
def postblog():
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
    print("Roster update initiated")
    ts = backend.getUpdateTimestamp()
    print(str(int(time.time()) - ts))

    # TODO also make a block in db to not allow multiple updates to run simultaneously
    if int(time.time()) - ts < 60:
        flash("It has been less than a minute since last update! Try again later")
        return "nothing"

    status = backend.updateRoster()
    print("Roster update returned with " + str(status))
    return "nothing"

@app.route('/addplayer', methods=['POST'])
def addPlayer():

    print("Received player addition request")
    playername = request.form["name"]
    playerclass = request.form["class"]
    playerrole = request.form["role"]


    print(playername)
    print(playerclass)
    print(playerclass)

    newplayer = {"name": playername, "Class": playerclass, "Role": playerrole}

    backend.addPlayer(newplayer)

    return redirect(url_for('admin'))

@app.route('/editplayer', methods=["POST"])
def editPlayer():
    attr = request.form["name"].split(",")
    role = request.form["role"]
    automated = False

    name = attr[0]

    if "automated-player" in attr:
        automated = True

    backend.editPlayerRole(name, role, automated)
        

    return redirect(url_for('admin'))
    



if __name__ == "__main__":
    app.run(debug=True)
