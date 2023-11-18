def test_ranking_85375():
    import pandas as pd
    from app.backend.ranking import ProviderRanker
    import numpy as np

    ground_truth = pd.read_csv("tests/ranking_85375.csv", index_col=0)
    ranker = ProviderRanker("app/backend/data/db.sqlite")
    result = ranker.rank("85375")

    for gt, res in zip(ground_truth.itertuples(), result.itertuples()):
        assert gt.id == res.id
        assert gt.name == res.name
        assert np.isclose(gt.rankingScore, res.rankingScore)
