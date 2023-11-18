import os
import pathlib
import sqlite3

import numpy as np
import pandas as pd


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
    postcodes: pd.DataFrame
    providers: pd.DataFrame
    qualities: pd.DataFrame

    # TODO better name
    def __init__(
        self,
        db_path: os.PathLike,
    ):
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self.__load_data()
        self.cache = Cache(128, self.postcodes)

    def __load_data(self) -> None:
        self.postcodes = pd.read_sql_query("SELECT * FROM postcode", self.db)
        self.postcodes.set_index("postcode", inplace=True)
        self.providers = pd.read_sql_query(
            "SELECT * FROM service_provider_profile", self.db
        )
        self.providers.set_index("id", inplace=True)
        self.qualities = pd.read_sql_query(
            "SELECT * FROM quality_factor_score", self.db
        )
        self.qualities.rename(columns={"profile_id": "id"}, inplace=True)
        self.qualities.set_index("id", inplace=True)
        # TODO update this on patch
        self.providers = pd.merge(self.providers, self.qualities, on="id")
        self.profile_scores = (
            0.4 * self.providers["profile_picture_score"]
            + 0.6 * self.providers["profile_description_score"]
        )

    def rank(self, postcode: str) -> pd.DataFrame:
        # TODO document
        result = self.cache[postcode]
        if result is not None:
            return result

        data = self.postcodes.loc[postcode]
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
        candidates["name"] = candidates["first_name"] + " " + candidates["last_name"]

        result = candidates.sort_values(by="rankingScore", ascending=False)[
            ["name", "rankingScore"]
        ]
        self.cache.insert(postcode, result)
        return result


class Cache:
    def __init__(self, max_size: int, postcodes: pd.DataFrame):
        self.max_size = max_size
        self.postcodes = postcodes
        # each entry in cache is another dict consisting of frequency and
        # result
        self.cache = {}

    def __getitem__(self, postcode):
        if postcode in self.cache:
            self.cache[postcode]["frequency"] += 1
            return self.cache[postcode]["result"]
        else:
            return None

    def _find_least_frequent_postcode(self):
        min_frequency = float("inf")
        min_postcode = None
        for postcode in self.cache:
            if self.cache[postcode]["frequency"] < min_frequency:
                min_frequency = self.cache[postcode]["frequency"]
                min_postcode = postcode
        return min_postcode

    def _remove_postcode(self, postcode):
        del self.cache[postcode]

    def insert(self, postcode, result):
        if len(self.cache) == self.max_size:
            postcode_to_remove = self._find_least_frequent_postcode()
            self._remove_postcode(postcode_to_remove)
        self.cache[postcode] = {"result": result, "frequency": 1}

    def on_update(self):
        self.cache = {}


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument("postcode", type=str, default="85375", nargs="?")
    args = parser.parse_args()
    db_path = pathlib.Path("app/backend/data/db.sqlite")
    start = time.perf_counter()
    ranker = ProviderRanker(db_path)
    print(f"Loading took {time.perf_counter() - start}s")
    start = time.perf_counter()
    results = ranker.rank(args.postcode)
    print(f"{len(results)} results in {(time.perf_counter() - start)*1e3}ms")
    print(results.iloc[:20])
