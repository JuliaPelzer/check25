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

bp = Blueprint("auth", __name__)


@bp.route("/", methods=(["GET", "POST"]))
def search():
    if request.method == "POST":
        postcode = request.form["postcode"]
        return redirect(url_for("auth.results", postalcode=postcode))

    return render_template("auth/search.html")


@bp.route("/details", methods=(["GET"]))
def details():
    return render_template("auth/details.html")


@bp.route("/results", methods=(["GET"]))
def results():
    return render_template("auth/results.html")
