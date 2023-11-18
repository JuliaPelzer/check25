from flask import (
    Blueprint,
    request,
)
from app import provider_ranker

bp = Blueprint("api", __name__)


@bp.route("/craftsmen", methods=["GET"])
def craftsmen():
    postalcode = request.args["postalcode"]
    print("test")
    result = provider_ranker.ranking_indices(postalcode)

    return str(result)


@bp.route("/craftman/<int:craftman_id>", methods=["PATCH"])
def craftman(craftman_id):
    # TODO: modify data

    return "craftman_id: " + str(craftman_id)
