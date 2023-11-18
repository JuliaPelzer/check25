from flask import (
    Blueprint,
    request,
    Response
)
from app import provider_ranker
from app.backend import interfaces

bp = Blueprint("api", __name__)


@bp.route("/craftsmen", methods=["GET"])
def craftsmen():
    postalcode = request.args["postalcode"]
    result_df = provider_ranker.rank(postalcode)
    result = interfaces.Response.from_df(result_df).to_json()

    return Response(result, mimetype="text/json")


@bp.route("/craftman/<int:craftman_id>", methods=["PATCH"])
def craftman(craftman_id):
    # TODO: modify data

    return "craftman_id: " + str(craftman_id)
