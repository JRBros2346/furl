import sqlite3
from flask import g, session
import hashlib, random, string

DATABASE = 'furl.db'  # Path to the SQLite database file

# Function to execute SQL queries
def query(query: str, params=()) -> sqlite3.Cursor:
    # Open a new database connection if not already present in the Flask global object 'g'
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)  # Connect to the database
        g.db.row_factory = sqlite3.Row  # Use Row factory to return rows as dict-like objects
    return g.db.cursor().execute(query, params)  # Execute query with parameters

# Function to hash passwords using SHA-256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()  # Return the hashed password

# Verify user credentials
def verify_user(username: str, password: str) -> bool:
    try:
        # Fetch the stored hashed password for the given username
        if query("SELECT password FROM users WHERE username = ?", (username,)).fetchone()[0] == hash_password(password):
            session['user'] = username  # Store username in session upon successful login
            print(f'{username} logged in..')
            return True
        else:
            return False  # Return False if the password does not match
    except TypeError:
        return False  # Return False if the username does not exist

# Create a new user account
def create_user(username: str, password: str) -> bool:
    # Check if the username already exists in the database
    if query("SELECT username FROM users WHERE username = ?", (username,)).fetchone() is None:
        # Insert the new user with hashed password
        query("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        print(f'Created new user {username}')
        return True
    else:
        return False  # Return False if username already exists

# Create a shortened URL (furl)
def create_furl(url: str, name: str, user: str) -> str:
    furl = generate_furl()  # Generate a unique shortened URL (furl)
    # Insert the furl data into the 'furled' table with initial count 0 and active status True
    query("INSERT INTO furled VALUES (?, ?, ?, ?, ?, ?)", (furl, url, name, user, 0, True))
    print(f'{user} created {name} ({furl}) for {url}')
    return furl  # Return the generated shortened URL

# Translate the furl to its original URL
def translate_furl(furl: str) -> str | None:
    # Fetch the original URL if the furl is active
    res = query("SELECT url FROM furled WHERE furl=? AND active=TRUE", (furl,)).fetchone()
    if res is None:
        return None  # Return None if the furl does not exist or is not active
    print(f'Redirecting to {res[0]}')
    return res[0]  # Return the original URL

# Mark the furl as visited by incrementing the visit count
def visited_furl(furl: str):
    query("UPDATE furled SET count=count+1 WHERE furl=?", (furl,))
    print(f'{furl} accessed..')

# Delete a shortened URL
def delete_furl(furl: str, user: str):
    # Delete the furl associated with the given user
    query("DELETE FROM furled WHERE furl=? AND user=?", (furl, user))
    print(f'{furl} deleted..')

# Deactivate a shortened URL
def deactivate_furl(furl: str, user: str):
    # Mark the furl as inactive for the given user
    query("UPDATE furled SET active=FALSE WHERE furl=? AND user=?", (furl, user))
    print(f'{furl} deactivated..')

# Reactivate a previously deactivated shortened URL
def activate_furl(furl: str, user: str):
    # Mark the furl as active for the given user
    query("UPDATE furled SET active=TRUE WHERE furl=? AND user=?", (furl, user))
    print(f'{furl} activated..')

# Fetch all furls associated with a user
def get_furls(user: str) -> dict[str, tuple[str, str, int, bool]]:
    # Return a dictionary of furls where each entry maps a furl to its associated data
    return {f[0]: f[1:] for f in query("SELECT furl, name, url, count, active FROM furled WHERE user=?", (user,)).fetchall()}

# Generate a unique furl (shortened URL) of a specified length (default 6 characters)
def generate_furl(length=6) -> str:
    while True:
        # Generate a random furl using letters and digits
        furl = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        # Ensure that the furl is unique and not one of the reserved routes
        if (furl,) not in query("SELECT furl FROM furled").fetchall() and furl not in {'signup', 'home', 'delete', 'activate', 'deactivate', 'logout'}:
            return furl  # Return the unique furl
