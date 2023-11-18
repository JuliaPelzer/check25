from dataclasses import dataclass, asdict
import json
import pandas as pd


@dataclass
class CraftsMan:
    id: int
    name: str
    rankingScore: float

    @staticmethod
    def from_row(row: pd.Series):
        return CraftsMan(row["id"], row["name"], row["rankingScore"])


@dataclass
class Response:
    craftsmen: list[CraftsMan]

    def from_df(df: pd.DataFrame):
        return Response([CraftsMan.from_row(row) for _, row in df.iterrows()])

    def to_json(self):
        return json.dumps(asdict(self))
