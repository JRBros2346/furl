from flask import Flask, render_template, request, redirect, url_for, session, json, abort,jsonify
from url_generator import save_url_to_json, load_user_urls
import os,hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
host = "http://127.0.0.1:5000/"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        u_name = request.form["username"]
        passwd = request.form["password"]

        if os.path.exists('user.json') and os.path.getsize('user.json') > 0:
            with open('user.json', 'r') as info:
                data = json.load(info)
                if u_name in data and data[u_name]['password'] == hash_password(passwd):
                    session['username'] = u_name
                    return redirect(url_for('home', username=u_name))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        u_name = request.form["username"]
        passwd = request.form["password"]

        encrypted_passwd = hash_password(passwd)
        if os.path.exists('user.json') and os.path.getsize('user.json') > 0:
            with open('user.json', 'r') as info:
                data = json.load(info)
        else:
            data = {}           
        if u_name not in data:
            data[u_name] = {'password': encrypted_passwd}
            with open('user.json', 'w') as info:
                json.dump(data, info, indent=4)
            return redirect(url_for('login'))

        return render_template("create_account.html", error="Username already exists")

    return render_template("create_account.html")

@app.route('/home/<username>', methods=['GET', 'POST'])
@app.route('/home/<username>', methods=['GET', 'POST'])
@app.route('/home/<username>', methods=['GET', 'POST'])
def home(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

    if request.method == "POST":
        url_received = request.form["lurl"]
        title = request.form["title"]
        print(f"Received URL to shorten: {url_received} with title: {title}")

        short_url = save_url_to_json(long_url=url_received, username=username, title=title)
        return render_template("home.html", short_url=host + short_url, username=username, history=load_user_urls(username), host=host)

    return render_template("home.html", username=username, history=load_user_urls(username), host=host)


@app.route('/<short_url>', methods=['GET'])
def redirecting(short_url):
    with open('urls.json', 'r') as file:
        data = json.load(file)
        if short_url in data:
            l_url = data[short_url].get('long_url')
            data[short_url]['count'] += 1
            
            with open('urls.json', 'w') as wf:
                json.dump(data, wf, indent=4)

            return redirect(l_url)
        else:
            abort(404, description="Short URL not found")


@app.route('/deactivate/<short_url>', methods=['POST'])
def deactivate_url(short_url):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    with open('urls.json', 'r') as file:
        data = json.load(file)
    
    # Ensure that only the URL created by the user is deactivated
    if short_url in data and data[short_url]['username'] == username:
        del data[short_url]
        
        with open('urls.json', 'w') as file:
            json.dump(data, file, indent=4)
    
    return redirect(url_for('home', username=username))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
