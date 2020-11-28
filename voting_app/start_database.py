import sqlalchemy as sqla
import csv
from environs import Env
import pandas as pd

def create_test_user():
    env = Env()
    env.read_env()

    db_url = env.str("DATABASE_URL")
    engine = sqla.create_engine(db_url, echo=True)

    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()


    voters = metadata.tables['voters']

    test_voter = voters.insert().values(first_name="FTest", last_name="LTest",
            otp="PASS1234", email="jefferson1990@yahoo.com",
            mobile="+639178589218", voted=False)

    with engine.connect() as conn:
        result = conn.execute(test_voter)
    print("Done.")

def load_users(file_path="./static/csv/db_users.csv"):
    print("Started...")
    env = Env()
    env.read_env()

    df_csv = pd.read_csv(file_path)
    df_csv['voted'] = False

    db_url = env.str("DATABASE_URL")
    engine = sqla.create_engine(db_url, echo=True)

    with engine.connect() as conn:
        df_csv.to_sql('voters', conn, if_exists='replace', index=True, index_label="id")
    print("Done.")
