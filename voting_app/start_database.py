import csv

import pandas as pd
import sqlalchemy as sqla

from environs import Env


def create_test_user(
    db_url=None,
    first_name="FTest",
    last_name="LTest",
    otp="PASS1234",
    email=None,
    mobile=None,
    voted=False,
):
    if not db_url:
        env = Env()
        env.read_env()
        db_url = env.str("DATABASE_URL")

    engine = sqla.create_engine(db_url, echo=True)

    metadata = sqla.MetaData()
    metadata.reflect(bind=engine)

    voters = metadata.tables["voters"]

    test_voter = voters.insert().values(
        first_name=first_name,
        last_name=last_name,
        otp=otp,
        email=email,
        mobile=mobile,
        voted=voted,
    )

    with engine.begin() as conn:
        conn.execute(test_voter)
    print("Done.")


def load_users(file_path="yearly_upload_files/db_users.csv", db_url=None):
    print("Started...")

    df_csv = pd.read_csv(file_path)

    required_columns = ["last_name", "first_name", "otp"]
    missing_required = [col for col in required_columns if col not in df_csv.columns]
    if missing_required:
        raise ValueError(f"Missing required column(s) in CSV: {', '.join(missing_required)}")

    for optional in ["email", "mobile"]:
        if optional not in df_csv.columns:
            df_csv[optional] = ""

    ordered_cols = ["last_name", "first_name", "email", "mobile", "otp"]
    df_csv = df_csv[ordered_cols]
    df_csv["voted"] = False

    if not db_url:
        env = Env()
        env.read_env()
        db_url = env.str("DATABASE_URL")
    engine = sqla.create_engine(db_url, echo=True)

    with engine.begin() as conn:
        df_csv.to_sql(
            "voters",
            conn,
            if_exists="replace",
            index=True,
            index_label="id",
        )
    print("Done.")
