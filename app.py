from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    json,
    abort,
    g,
    jsonify,
)
import db

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Secret key for session management
HOST = "0.0.0.0"
PORT = 5000

# Enable foreign key constraints in the SQLite database when app context is available
with app.app_context():
    db.query("PRAGMA FOREIGN_KEYS=ON")


# Login route
# Handles both GET (render login page) and POST (login form submission) requests
@app.route("/", methods=["GET", "POST"])
def login() -> str:
    if request.method == "POST":  # If user submits login form
        username = request.form["username"]
        password = request.form["password"]

        # Verify user credentials using db.verify_user
        if db.verify_user(username, password):
            # If valid, redirect to the home page
            return redirect(url_for("home", username=username))
        # Render login page with error message for invalid credentials
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")  # Render login page on GET request


# Signup route
# Allows new users to create an account
@app.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    if request.method == "POST":  # If user submits signup form
        username = request.form["username"]
        password = request.form["password"]

        # Attempt to create a new user with db.create_user
        if db.create_user(username, password):
            return redirect(url_for("login"))  # Redirect to login on success
        return render_template(
            "signup.html", error="Username already exists"
        )  # Error on username collision
    return render_template("signup.html")  # Render signup page on GET request


# Home route for logged-in users
# Displays shortened URLs and handles new URL shortening requests
@app.route("/home/<username>", methods=["GET", "POST"])
def home(username: str) -> str:
    # Ensure the user is logged in by checking the session
    if "user" not in session or session["user"] != username:
        return redirect(url_for("login"))  # Redirect to login if user is not logged in

    if request.method == "POST":  # If user submits a URL shortening request
        url = request.form["url"]
        name = request.form["name"]
        print(f"Received URL to shorten: {url} with name: {name}")

        # Create a shortened URL (furl) and store it in the database
        furl = db.create_furl(url, name, username)
        print(db.get_furls(username))  # Debugging: Print all user's URLs

        # Render home page with updated list of shortened URLs
        return render_template(
            "home.html",
            username=username,
            furl=furl,
            furls=db.get_furls(username),
            host=HOST,
        )

    # Render home page with list of user's shortened URLs on GET request
    return render_template("home.html", username=username, furls=db.get_furls(username))


# Redirection route for shortened URLs
# Takes a furl (short URL) and redirects the user to the original URL
@app.route("/<furl>", methods=["GET"])
def redirecting(furl: str) -> str:
    res = db.translate_furl(furl)  # Translate the short URL to the original
    if res is not None:
        db.visited_furl(furl)  # Mark the URL as visited in the database
        return redirect(res)  # Redirect to the original URL
    else:
        abort(
            404, description="Short URL not found"
        )  # Return 404 if short URL is invalid


# Delete a shortened URL
# Requires the user to be logged in, then removes the URL from their account
@app.route("/delete/<furl>", methods=["POST"])
def delete_furl(furl: str) -> str:
    if "user" not in session:  # Check if user is logged in
        return redirect(url_for("login"))

    username = session["user"]
    db.delete_furl(furl, username)  # Remove the URL from the database
    return redirect(url_for("home", username=username))  # Redirect to home page


# Deactivate a shortened URL
# Disables the URL without deleting it, making it temporarily unusable
@app.route("/deactivate/<furl>", methods=["POST"])
def deactivate_furl(furl: str) -> str:
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    db.deactivate_furl(furl, username)  # Deactivate the URL
    return redirect(url_for("home", username=username))  # Redirect to home page


# Activate a previously deactivated shortened URL
@app.route("/activate/<furl>", methods=["POST"])
def activate_furl(furl: str) -> str:
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    db.activate_furl(furl, username)  # Reactivate the URL
    return redirect(url_for("home", username=username))  # Redirect to home page


# Logout route
# Logs the user out by clearing the session
@app.route("/logout")
def logout() -> str:
    session.pop("user", None)  # Remove 'user' from the session
    return redirect(url_for("login"))  # Redirect to login page


# Close the database connection when the app context is destroyed
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.commit()  # Commit any pending transactions
        db.close()  # Close the connection


# Run the Flask app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True, port=PORT, host=HOST)
