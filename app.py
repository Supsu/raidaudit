"""
Root module for Raid audit

app.py handles flask routes, flask configuration, gathering data to display from backend module(s)
and rendering html templates to response.

Routes are documented with their respective methods. Omitted from docstrings of single routes
is that every route that corresponds to a rendered template also runs backend.getSideBar() to
fill the left panel with data.
"""
from flask import Flask, session, redirect, url_for, request, render_template, flash
from dotenv import load_dotenv
from backend import Backend
import time
import subprocess
import json
import os

version = ""
try:
    version = str(subprocess.check_output(["git", "describe", "--all", "--always", "HEAD"]).strip())
except:
    version = "N/A"
print(version)

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

# subtitle for template
sub = "{} | {}-{}".format(os.getenv("WOWGUILD"), os.getenv("WOWREALM"), os.getenv("WOWREGION"))

backend = Backend()


@app.route('/')
def index():
    """
    Responds to route '/'.
    
    Gets data required for index page from backend.getView(), backend.getLogs(), calculates time from last update of roster
    and returns flask.render_template('index.html') with required data. 
    """

    sidebar = backend.getSideBar()
    sidebar[1] = {"version": version}
    roster = backend.getView()
    logs = backend.getLogs()
    user = None

    # get data to generate links in roster table
    linkdata = json.dumps(backend.getLinkInfo())

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
        updated = time.strftime("%d days, %H hours, %M minutes, %S seconds ago", time.gmtime(delta))

    if 'username' in session:
        user = session['username']
    return render_template('index.html', sub=sub, user=user, data=roster, logs=logs, updated=updated, sidebar=sidebar, linkdata=linkdata)


@app.route('/blog')
@app.route('/blog/<int:id>')
def blog(id=None):
    """
    Responds to routes '/blog' and '/blog/id'.
    
    If no ID is given returns blog posts
    gotten from backeng.getBlog() and with ID backend.getSingleBlog(id). Returns 
    flask.render_template('blog.html') with required data.
    """

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
    """
    Responds to route '/admin'. 
    
    Gets player data from backend.getView() and uses flask.render_template('admin.html') to
    render admin page for logged in user. If there is no session that has username recorded,
    instead redirects to render 'index'.
    """

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
    """
    Responds to route '/post' [POST ONLY]

    POST only method. Takes POST data from request and sends it to
    backend.post() to store a new blog post into database.
    """

    r=backend.post(request.form['title'], request.form['post'])
    if r:
        flash("Success!")
    else:
        flash("Failure!")
        
    return redirect(url_for('admin'))

@app.route('/login', methods=['POST'])
def login():
    """
    Responds to route '/login' [POST ONLY]

    POST only method. Takes input from login form and check login credentials
    against known login credentials from database. If login is succesfull,
    inputs username to session['username'], otherwise redirects to 'index'.
    """

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
    """
    Responds to route '/logout'

    Uses session.pop('username') to logout current user.
    """
    session.pop('username')
    return redirect(url_for('index'))

@app.route('/update')
def updateIndex():
    """
    Responds to route '/update'

    This route/method is used to initiate roster update process. Gets time from latest update
    with backend.getUpdateTimestamp() and time.time(), and if under a minute doesn't continue with
    updating. Otherwise runs backend.updateRoster().
    """

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
    """
    Responds to route '/addplayer' [POST ONLY]

    Post only route used to add players to database from admin page. Gets players
    name, role and class from form, then calls backend.addPlayer() to add player to DB.
    """

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
    """
    Responds to  route '/editplayer' [POST ONLY]

    Post only method/route that is used to edit existing player roles from admin page.
    Gets characters name and role from form, distinguishes between automatically and manually added
    characters via form data and calls backend.editPlayerRole().
    """

    attr = request.form["name"].split(",")
    role = request.form["role"]
    automated = False

    name = attr[0]

    if "automated-player" in attr:
        automated = True

    if request.form["submitButton"] == "add":
        backend.editPlayerRole(name, role, automated)
    elif request.form["submitButton"] == "delete":
        player = {
            "name": name,
            "automated": automated
        }
        print("Deleting player: " + str(player))

        r = backend.removePlayer(player)

    else:
        print("Edit bork")
        

    return redirect(url_for('admin'))
    



if __name__ == "__main__":
    app.run(debug=True)
