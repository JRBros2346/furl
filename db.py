import sqlite3
from flask import g
import random, string

DATABASE = "furl.db"


def query(query: str, params=()) -> sqlite3.Cursor:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db.execute(query, params)


def create_furl(url: str, name: str) -> str:
    furl = generate_furl()
    query("INSERT INTO furled VALUES (?, ?, ?, ?)", (furl, url, name, 0))
    print(f"Created {name} ({furl}) for {url}")
    return furl


def translate_furl(furl: str) -> str | None:
    try:
        url = query("SELECT url FROM furled WHERE furl=?", (furl,)).fetchone()[0]
        query("UPDATE furled SET count=count+1 WHERE furl=?", (furl,))
        print(f"Redirecting to {url}")
        return url
    except IndexError:
        return None


def delete_furl(furl: str):
    query("DELETE FROM furled WHERE furl=?", (furl,))
    print(f"{furl} deleted..")


def get_furls() -> dict[str, tuple[str, int]]:
    return {
        f[0]: f[1:] for f in query("SELECT furl, name, count FROM furled").fetchall()
    }


def generate_furl(length=6) -> str:
    while True:
        furl = "".join(random.choices(string.ascii_letters + string.digits, k=length))
        if furl not in get_furls().keys() and furl != "api":
            return furl
