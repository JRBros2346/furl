import sqlite3
from flask import g, session
import hashlib, random, string

DATABASE = 'furl.db'

def query(query, params=()) -> sqlite3.Cursor:
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db.cursor().execute(query, params)

def hash_password(password) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password) -> bool:
    if query("SELECT password FROM users WHERE username = ?", (username,)).fetchone()[0]==hash_password(password):
        session['user'] = username
        return True
    else:
        return False

def create_user(username, password) -> bool:
    if query("SELECT username FROM users WHERE username = ?", (username,)).fetchone()==None:
        query("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        return True
    else:
        return False

def create_furl(url, name, user) -> str:
    furl = generate_furl()
    query("INSERT INTO furled VALUES (?, ?, ?, ?, ?, ?)", (furl, url, name, user, 0, True))
    return furl

def translate_furl(furl) -> str|None:
    res = query("SELECT url FROM furled WHERE furl=?", (furl,)).fetchone()
    if res is None:
        return None
    return res[0]

def delete_furl(furl, user):
    query("DELETE FROM furled WHERE furl=? AND user=?", (furl, user))

def deactivate_furl(furl, user):
    query("UPDATE furled SET active=FALSE WHERE furl=? AND user=?", (furl, user))

def activate_furl(furl, user):
    query("UPDATE furled SET active=TRUE WHERE furl=? AND user=?", (furl, user))


def get_furls(user) -> dict:
    return {f[0]:f[1:] for f in query("SELECT * FROM furled WHERE user=?", (user,)).fetchall()}

def generate_furl(length=6):
    while True:
        furl = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if (furl,) not in query("SELECT furl FROM furled").fetchall() and furl not in {'signup', 'home', 'delete', 'activate', 'deactivate', 'logout'}:
            return furl