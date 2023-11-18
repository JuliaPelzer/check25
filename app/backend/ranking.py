import os
import pathlib
import sqlite3
from collections import deque
from functools import lru_cache

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
    R = 6371  # radius of the earth in km
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
        # utilize a database for persistent memory, since it is better to
        # update than to write a new json file at every update.
        # For the efficiency of the ranking, the data is loaded into memory.
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.__load_data()

    def __load_data(self) -> None:
        """Loads postcodes, providers and qualities from the database into
        memory.
        """

        # create postcodes dataframe
        self.postcodes = pd.read_sql_query("SELECT * FROM postcode", self.db)
        self.postcodes.set_index("postcode", inplace=True)
        self.providers = pd.read_sql_query(
            "SELECT * FROM service_provider_profile", self.db
        )
        # create providers dataframe
        self.providers.set_index("id", inplace=True)
        self.qualities = pd.read_sql_query(
            "SELECT * FROM quality_factor_score", self.db
        )
        # create qualities dataframe and precompute profile_scores
        self.qualities.rename(columns={"profile_id": "id"}, inplace=True)
        self.qualities.set_index("id", inplace=True)
        self.providers = pd.merge(self.providers, self.qualities, on="id")
        self.profile_scores = (
            0.4 * self.providers["profile_picture_score"]
            + 0.6 * self.providers["profile_description_score"]
        )

    def get_Patch_Response(self, craftsman_id: int) -> dict:
        return dict(
            id=craftsman_id,
            updated=dict(
                maxDrivingDistance=int(
                    self.providers.at[craftsman_id, "max_driving_distance"]
                ),
                profilePictureScore=int(
                    self.providers.at[craftsman_id, "profile_picture_score"]
                ),
                profileDescriptionScore=int(
                    self.providers.at[craftsman_id, "profile_description_score"]
                ),
            ),
        )

    def __update_local(
        self,
        craftsman_id: int,
        profile_picture_score: float = None,
        profile_description_score: float = None,
        max_driving_distance: float = None,
    ) -> None:
        """Update a providers dataframe entry for a given craftsman_id.

        Args:
            craftsman_id (int)
            profile_picture_score (float, optional): Defaults to None.
            profile_description_score (float, optional): Defaults to None.
            max_driving_distance (float, optional): Defaults to None.
        """
        if max_driving_distance is not None:
            self.providers.at[
                craftsman_id, "max_driving_distance"
            ] = max_driving_distance
        if profile_description_score is not None:
            self.providers.at[
                craftsman_id, "profile_description_score"
            ] = profile_description_score
        if profile_picture_score is not None:
            self.providers.at[
                craftsman_id, "profile_picture_score"
            ] = profile_picture_score

        # recompute profile_description_score
        if profile_description_score is not None or profile_picture_score is not None:
            self.profile_scores.at[craftsman_id] = (
                0.4 * self.providers.at[craftsman_id, "profile_picture_score"]
                + 0.6 * self.providers.at[craftsman_id, "profile_description_score"]
            )

    def __update_db(
        self,
        craftsman_id: int,
        profile_picture_score: float = None,
        profile_description_score: float = None,
        max_driving_distance: float = None,
    ) -> None:
        """Update entry in service_provider_profile with craftsman_id.

        Args:
            craftsman_id (int)
            profile_picture_score (float, optional): Defaults to None.
            profile_description_score (float, optional): Defaults to None.
            max_driving_distance (float, optional): Defaults to None.
        """
        if max_driving_distance is not None:
            self.db.execute(
                "UPDATE service_provider_profile SET max_driving_distance = ? WHERE id = ?",
                (max_driving_distance, craftsman_id),
            )
        if profile_description_score is not None:
            self.db.execute(
                "UPDATE quality_factor_score SET profile_description_score = ? WHERE profile_id = ?",
                (profile_description_score, craftsman_id),
            )
        if profile_picture_score is not None:
            self.db.execute(
                "UPDATE quality_factor_score SET profile_picture_score = ? WHERE profile_id = ?",
                (profile_picture_score, craftsman_id),
            )
        self.db.commit()

    def update(
        self,
        craftsman_id: int,
        profile_picture_score: float = None,
        profile_description_score: float = None,
        max_driving_distance: float = None,
    ) -> None:
        """Update caftsman entry both in database and dataframe.

        Args:
            craftsman_id (int)
            profile_picture_score (float, optional): Defaults to None.
            profile_description_score (float, optional): Defaults to None.
            max_driving_distance (float, optional): Defaults to None.
        """
        self.__update_local(
            craftsman_id,
            profile_picture_score,
            profile_description_score,
            max_driving_distance,
        )
        self.__update_db(
            craftsman_id,
            profile_picture_score,
            profile_description_score,
            max_driving_distance,
        )
        self.rank.cache_clear()

    @lru_cache(maxsize=128)
    def rank(self, postcode: str) -> pd.DataFrame:
        """Calculates rank for all craftsmen who are in reach of a given
        postcode and returns them as a dataframe in ascending order.

        Args:
            postcode (str): client postcode

        Returns:
            pd.DataFrame: all craftsmen in reach of the postcode, sorted by
            rank in ascending order.
        """
        # TODO document

        # load row from postcode table for which to calculate the ranking
        data = self.postcodes.loc[postcode]
        driving_distance_bonus = 0
        if data["postcode_extension_distance_group"] == "group_b":
            driving_distance_bonus = 2
        elif data["postcode_extension_distance_group"] == "group_c":
            driving_distance_bonus = 5

        # calculate distance between postcode and all providers
        distances = dist(
            data["lat"], data["lon"], self.providers["lat"], self.providers["lon"]
        )

        # max_driving_distance is in meters, everything else in km
        max_distance_mask = (
            distances
            < self.providers["max_driving_distance"] / 1000 + driving_distance_bonus
        )
        default_distance = 80

        # only calculate ranks for providers that are in range (i.e. have a
        # True max_distance_mask value)
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

        # to avoid SettingWithCopyWarning explicitly copy the relevant columns
        candidates = self.providers[max_distance_mask].copy()
        candidates["rankingScore"] = ranks
        candidates["name"] = candidates["first_name"] + " " + candidates["last_name"]

        result = candidates.sort_values(by="rankingScore", ascending=False)[
            ["name", "rankingScore"]
        ]
        return result


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument("postcode", type=str, default="85375", nargs="?")
    args = parser.parse_args()
    db_path = pathlib.Path("app/backend/data/db.sqlite")
    start = time.perf_counter()
    ranker = ProviderRanker(db_path)
    print(f"Loading took {(time.perf_counter() - start)*1e3:.2f}ms")
    start = time.perf_counter()
    results = ranker.rank(args.postcode)
    print(f"{len(results)} results in {(time.perf_counter() - start)*1e3:.2f}ms")
    print(results.iloc[:20])
