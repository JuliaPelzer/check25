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

    def _ranking_indices(self, postcode):
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
        # TODO remove where driving distance > MAX_DRIVING_DISTANCE
        default_distance = 80
        distance_scores = 1 - (distances / (default_distance + driving_distance_bonus))
        distance_weight = np.where(distances > default_distance, 0.01, 0.15)
        ranks = (
            distance_weight * distance_scores
            + (1 - distance_weight) * self.profile_scores
        )
        ranks: pd.DataFrame = ranks.to_numpy()
        # TODO maybe sort differently if indices are not conserved
        ranking = np.argsort(ranks)[::-1]
        return ranking

    def providers(self, indices):
        self.providers.iloc[indices]
