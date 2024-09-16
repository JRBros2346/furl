from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    abort,
    g,
)
import db

app = Flask(__name__)
HOST = "0.0.0.0"
PORT = 5000

with app.app_context():
    db.query("PRAGMA FOREIGN_KEYS=ON")


@app.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "POST":
        url = request.form["url"]
        name = request.form["name"]
        db.create_furl(url, name)
    return render_template("home.html.jinja", furls=db.get_furls())


@app.route("/<furl>", methods=["GET"])
def redirecting(furl: str) -> str:
    res = db.translate_furl(furl)
    if res is not None:
        return redirect(res)
    else:
        abort(404, description="Short URL not found")


@app.route("/api/delete/<furl>", methods=["POST"])
def delete_furl(furl: str) -> str:
    db.delete_furl(furl)
    return redirect(url_for("home"))


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.commit()
        db.close()


if __name__ == "__main__":
    app.run(debug=True, port=PORT, host=HOST)
