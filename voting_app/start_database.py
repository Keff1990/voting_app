import sqlalchemy as sqla
import csv
from environs import Env
import pandas as pd

def create_test_user(db_url=None, first_name="FTest", last_name="LTest", otp="PASS1234", email=None, mobile=None, voted=False):
    if not db_url:
        env = Env()
        env.read_env()
        db_url = env.str("DATABASE_URL")

    engine = sqla.create_engine(db_url, echo=True)

    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()


    voters = metadata.tables['voters']

    test_voter = voters.insert().values(first_name=first_name, last_name=last_name,
            otp=otp, email=email,
            mobile=mobile, voted=voted)

    with engine.connect() as conn:
        result = conn.execute(test_voter)
    print("Done.")

def load_users(file_path="./db_users.csv", db_url=None):
    print("Started...")

    df_csv = pd.read_csv(file_path)
    df_csv['voted'] = False

    if not db_url:
        env = Env()
        env.read_env()
        db_url = env.str("DATABASE_URL")
    engine = sqla.create_engine(db_url, echo=True)

    with engine.connect() as conn:
        df_csv.to_sql('voters', conn, if_exists='replace', index=True, index_label="id")
    print("Done.")
