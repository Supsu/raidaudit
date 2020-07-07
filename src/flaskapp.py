from flask import Flask, session, redirect, url_for, request, render_template
from dotenv import load_dotenv
from backend import Backend

app = Flask(__name__)

app.secret_key = b'uaiYSaYISUS41567YDabhY&WQT23YTEEiubz'

#subtitle for template
sub = "Pulumafia (H) | Stormscale-EU"

backend = Backend()

@app.route('/')
def index():
    roster = backend.getView()
    logs = backend.getLogs()
    return render_template('index.html', sub=sub, data=roster, logs=logs)

@app.route('/blog')
@app.route('/blog/<id>')
def blog():
    return render_template('blog.html', sub=sub)

@app.route('/admin')
def admin():
    return render_template('admin.html', sub=sub)



if __name__ == "__main__":
    app.run(port=1337, debug=True, host="0.0.0.0")