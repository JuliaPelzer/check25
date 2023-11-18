import pathlib
import sqlite3

import pandas as pd

if __name__ == "__main__":
    schema = pathlib.Path("app/backend/data/schema.sql")
    db = pathlib.Path("app/backend/data/db.sqlite")
    if db.exists():
        db.unlink()
    with open(schema) as f:
        sql = f.read()
    conn = sqlite3.connect(db)
    conn.executescript(sql)
    conn.commit()
    postcodes = pathlib.Path("app/backend/data/postcode.json")
    providers = pathlib.Path("app/backend/data/service_provider_profile.json")
    qualities = pathlib.Path("app/backend/data/quality_factor_score.json")
    pd.read_json(postcodes, dtype={"postcode": "str"}).to_sql(
        "postcode", conn, schema=sql, if_exists="append", index=False
    )
    pd.read_json(providers).to_sql(
        "service_provider_profile", conn, schema=sql, if_exists="append", index=False
    )
    pd.read_json(qualities).to_sql(
        "quality_factor_score", conn, schema=sql, if_exists="append", index=False
    )
