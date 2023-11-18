import pandas as pd
import numpy as np
import pathlib
import os
import sqlite3


def dist(
    lat_point: float,
    lon_point: float,
    lat_providers: pd.DataFrame,
    lon_providers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate all distances between a coordinate and a list of coordinates.

    Parameters
    ----------
    lat_postcode : float
        Latitude of the postcode
    lon_postcode : float
        Longitude of the postcode
    lat_providers : pd.DataFrame
        Latitudes of the providers
    lon_providers : pd.DataFrame
        Longitudes of the providers
    """
    R = 6371  # radius of the earth in m
    # adapted from http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
    return (
        np.arccos(
            np.sin(lat_point) * np.sin(lat_providers)
            + np.cos(lat_point)
            * np.cos(lat_providers)
            * np.cos(lon_point - lon_providers)
        )
        * R
    )


class ProviderRanker:
    db_path: os.PathLike
    db: sqlite3.Connection

    # TODO better name
    def __init__(
        self,
        db_path: os.PathLike,
    ):
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self.__load_data()

    def __load_data(self) -> None:
        self.postcodes = pd.read_sql_query("SELECT * FROM postcode", self.db)
        self.providers = pd.read_sql_query(
            "SELECT * FROM service_provider_profile", self.db
        )
        self.qualities = pd.read_sql_query(
            "SELECT * FROM quality_factor_score", self.db
        )
        # TODO update this on patch
        self.providers.rename(columns={"id": "profile_id"}, inplace=True)
        self.providers = pd.merge(self.providers, self.qualities, on="profile_id")
        self.profile_scores = (
            0.4 * self.providers["profile_picture_score"]
            + 0.6 * self.providers["profile_description_score"]
        )

    def ranking_indices(self, postcode):
        # TODO document
        data = self.postcodes[self.postcodes["postcode"] == postcode].iloc[0]
        driving_distance_bonus = 0
        if data["postcode_extension_distance_group"] == "group_b":
            driving_distance_bonus = 2
        elif data["postcode_extension_distance_group"] == "group_c":
            driving_distance_bonus = 5
        distances = dist(
            data["lat"], data["lon"], self.providers["lat"], self.providers["lon"]
        )

        # max_driving_distance is in meters, everything else in km
        max_distance_mask = (
            distances
            < self.providers["max_driving_distance"] / 1000 + driving_distance_bonus
        )
        default_distance = 80
        distance_scores = 1 - (
            distances[max_distance_mask] / (default_distance + driving_distance_bonus)
        )
        distance_weight = np.where(
            distances[max_distance_mask] > default_distance, 0.01, 0.15
        )
        ranks: pd.DataFrame = (
            distance_weight * distance_scores
            + (1 - distance_weight) * self.profile_scores[max_distance_mask]
        )
        candidates = self.providers[max_distance_mask].copy()
        candidates["rankingScore"] = ranks
        candidates.rename(columns={"profile_id": "id"}, inplace=True)
        candidates["name"] = candidates["first_name"] + " " + candidates["last_name"]

        return candidates.sort_values(by="rankingScore", ascending=False)[
            ["id", "name", "rankingScore"]
        ]


if __name__ == "__main__":
    db_path = pathlib.Path("app/backend/data/db.sqlite")
    ranker = ProviderRanker(db_path)
    results = ranker.ranking_indices("85375")
    print(results.iloc[:20])
