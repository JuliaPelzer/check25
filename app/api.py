from flask import (
    Blueprint,
    request,
)
from app import provider_ranker
from app.backend.interfaces import Response

bp = Blueprint("api", __name__)


@bp.route("/craftsmen", methods=["GET"])
def craftsmen():
    postalcode = request.args["postalcode"]
    print("test")
    result_df = provider_ranker.rank(postalcode)
    result = Response.from_df(result_df).to_json()

    return str(result)


@bp.route("/craftman/<int:craftman_id>", methods=["PATCH"])
def craftman(craftman_id):
    # TODO: modify data

    return "craftman_id: " + str(craftman_id)
