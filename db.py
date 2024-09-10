import sqlite3
from flask import g, session
import hashlib, random, string

DATABASE = 'furl.db'

def query(query: str, params=()) -> sqlite3.Cursor:
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db.cursor().execute(query, params)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username: str, password: str) -> bool:
    try:
        if query("SELECT password FROM users WHERE username = ?", (username,)).fetchone()[0]==hash_password(password):
            session['user'] = username
            print(f'{username} logged in..')
            return True
        else:
            return False
    except TypeError:
        return False

def create_user(username: str, password: str) -> bool:
    if query("SELECT username FROM users WHERE username = ?", (username,)).fetchone()==None:
        query("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        print(f'Created new user {username}')
        return True
    else:
        return False

def create_furl(url: str, name: str, user: str) -> str:
    furl = generate_furl()
    query("INSERT INTO furled VALUES (?, ?, ?, ?, ?, ?)", (furl, url, name, user, 0, True))
    print(f'{user} created {name} ({furl}) for {url}')
    return furl

def translate_furl(furl: str) -> str | None:
    res = query("SELECT url FROM furled WHERE furl=? AND active=TRUE", (furl,)).fetchone()
    if res is None:
        return None
    print(f'Redirecting to {res[0]}')
    return res[0]

def visited_furl(furl: str):
    query("UPDATE furled SET count=count+1 WHERE furl=?", (furl,))
    print(f'{furl} accessed..')

def delete_furl(furl: str, user: str):
    query("DELETE FROM furled WHERE furl=? AND user=?", (furl, user))
    print(f'{furl} deleted..')

def deactivate_furl(furl: str, user: str):
    query("UPDATE furled SET active=FALSE WHERE furl=? AND user=?", (furl, user))
    print(f'{furl} deactivated..')

def activate_furl(furl: str, user: str):
    query("UPDATE furled SET active=TRUE WHERE furl=? AND user=?", (furl, user))
    print(f'{furl} activated..')

def get_furls(user: str) -> dict[str, tuple[str, str, int, bool]]:
    return {f[0]:f[1:] for f in query("SELECT furl, name, url, count, active FROM furled WHERE user=?", (user,)).fetchall()}

def generate_furl(length=6) -> str:
    while True:
        furl = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if (furl,) not in query("SELECT furl FROM furled").fetchall() and furl not in {'signup', 'home', 'delete', 'activate', 'deactivate', 'logout'}:
            return furl