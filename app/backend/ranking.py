import json
import pandas as pd
import numpy as np
import pathlib
import os


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
    provider_json: os.PathLike
    postcodes_json: os.PathLike
    qualities_json: os.PathLike
    providers: pd.DataFrame
    postcodes: pd.DataFrame

    # TODO better name
    def __init__(
        self,
        provider_json: os.PathLike,
        postcodes_json: os.PathLike,
        qualities_json: os.PathLike,
    ):
        self.provider_json = provider_json
        self.postcodes_json = postcodes_json
        self.qualities_json = qualities_json
        self.__load_data()

    def __load_data(self) -> None:
        with open(self.provider_json, encoding="utf-8") as f:
            self.providers = pd.DataFrame(json.loads(f.read()))
        with open(self.postcodes_json, encoding="utf-8") as f:
            self.postcodes = pd.DataFrame(json.loads(f.read()))
        with open(self.qualities_json, encoding="utf-8") as f:
            self.qualities = pd.DataFrame(json.loads(f.read()))
        # TODO update this on catch
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
    data_dir = pathlib.Path("app/backend/data")
    ranker = ProviderRanker(
        data_dir / "service_provider_profile.json",
        data_dir / "postcode.json",
        data_dir / "quality_factor_score.json",
    )
    results = ranker.ranking_indices("85375")
    print(results.iloc[:20])
