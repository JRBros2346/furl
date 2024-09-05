from flask import Flask, render_template, request, json, redirect, session, url_for, abort
from url_generator import save_url_to_json
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 
host = "http://127.0.0.1:5000/"

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        u_name = request.form["username"]
        passwd = request.form["password"]
        with open('user.json', 'r') as info:
            data = json.load(info)
            if u_name in data and check_password_hash(data[u_name]['password'], passwd):
                session['username'] = u_name
                return redirect(url_for('home'))
            else:
                error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        u_name = request.form['username']
        passwd = request.form['password']
        hashed_passwd = generate_password_hash(passwd)
        
        with open('user.json', 'r+') as info:
            data = json.load(info)
            if u_name not in data:
                data[u_name] = {'password': hashed_passwd}
                info.seek(0)
                json.dump(data, info, indent=4)
                return redirect(url_for('login'))
            else:
                return "Username already exists. Try another one."
    
    return render_template('create_account.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login')) 
    
    if request.method == "POST":
        url_received = request.form["lurl"]
        short_url = save_url_to_json(url_received, session['username'])
        return render_template('home.html', short_url=host + short_url)
    else:
        return render_template("home.html")

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


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=2006)
