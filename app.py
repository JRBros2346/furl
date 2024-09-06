from flask import Flask, render_template, request, redirect, url_for, session, json, abort, g, jsonify
from url_generator import save_url_to_json, load_user_urls
import db

app = Flask(__name__)
app.secret_key = 'your_secret_key'
HOST = "127.0.0.1"
PORT = 5000


with app.app_context():
    db.query('PRAGMA FOREIGN_KEYS=ON')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if db.verify_user(username, password):
            return redirect(url_for('home', username=username))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        if db.create_user(username, password):
            return redirect(url_for('login'))
        return render_template("signup.html", error="Username already exists")
    return render_template("signup.html")

@app.route('/home/<username>', methods=['GET', 'POST'])
def home(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if request.method == "POST":
        url = request.form["url"]
        name = request.form["name"]
        print(f"Received URL to shorten: {url} with name: {name}")

        furl = db.create_furl(url, name, username)
        # return render_template("home.html", username=username, furl=f'{HOST}/{furl}', furls=db.get_furls(username), host=HOST)
        return jsonify(db.get_furls(username))

    return render_template("home.html", username=username, furls=db.get_furls(username), host=HOST)

@app.route('/<furl>', methods=['GET'])
def redirecting(furl):
    res = db.translate_furl()
    if res is not None:
        return redirect(res)
    else:
        abort(404, description="Short URL not found")


@app.route('/delete/<furl>', methods=['POST'])
def delete_furl(furl):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    db.delete_furl(furl)
    return redirect(url_for('home', username=username))

@app.route('/deactivate/<furl>', methods=['POST'])
def deactivate_furl(furl):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    db.deactivate_furl(furl)
    
    return redirect(url_for('home', username=username))

@app.route('/activate/<furl>', methods=['POST'])
def activate_furl(furl):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']
    db.activate_furl(furl)
    
    return redirect(url_for('home', username=username))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host=HOST)