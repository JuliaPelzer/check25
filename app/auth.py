import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint("auth", __name__)


@bp.route("/", methods=("GET", "POST"))
def search():
    if request.method == "POST":
        postcode = request.form["postcode"]
        db = get_db()
        error = None

        if error is None:
            # TODO call stuff
            return render_template("auth/results.html")


        flash(error)

    return render_template("auth/search.html")



@bp.route("/details", methods=("GET", "POST"))
def details():
    return render_template("auth/details.html")


# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get("user_id")

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = (
#             get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
#         )


# @bp.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("index"))


# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for("auth.login"))

#         return view(**kwargs)

#     return wrapped_view
