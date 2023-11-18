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


@bp.route("/", methods=(["GET"]))
def search():
    if request.method == "POST":
        postcode = request.form["postcode"]
        db = get_db()
        error = None

        if error is None:
            # TODO call stuff
            return redirect(url_for("auth.results"))


        flash(error)

    return render_template("auth/search.html")



@bp.route("/details", methods=(["GET"]))
def details():
    return render_template("auth/details.html")

@bp.route("/results", methods=(["GET"]))
def results():
    return render_template("auth/results.html")
