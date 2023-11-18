from flask import Blueprint, flash, g, render_template, request, url_for, session
import pathlib

bp = Blueprint("api", __name__)
from app.backend.ranking import ProviderRanker


def get_rank():
    if "rank" not in g:
        data_dir = pathlib.Path("app/backend/data")
        g.rank = ProviderRanker(
            data_dir / "service_provider_profile.json",
            data_dir / "postcode.json",
            data_dir / "quality_factor_score.json",
        )

    return g.rank


@bp.route("/craftsmen", methods=["GET"])
def craftsmen():
    postalcode = request.args["postalcode"]
    ranking = get_rank()
    result = ranking.ranking_indices(postalcode)
    
    return str(result)


@bp.route("/craftman/<int:craftman_id>", methods=["PATCH"])
def craftman(craftman_id):

    return "craftman_id: " + str(craftman_id)