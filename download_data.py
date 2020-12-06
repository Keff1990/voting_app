import pandas as pd
from datetime import datetime
import sqlalchemy as sqla
from sqlalchemy.sql import select
from sqlalchemy import func

def download_data(db_url):

    now = datetime.now().strftime('%Y-%m-%d-%H-%M')
    db_url = "sqlite:///" + db_url
    engine = sqla.create_engine(db_url, echo=True)

    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()

    Vote = metadata.tables['votes']
    Voter = metadata.tables['voters']

    s = select([Vote.c.type, Vote.c.name, func.count(Vote.c.name)]).group_by(Vote.c.name)
    with engine.connect() as conn:
        result = conn.execute(s)

        df=pd.DataFrame(result, columns=['type', 'name', 'votes'])

    df.to_csv(f"votes_{now}.csv")

    s = select([Voter.c.first_name, Voter.c.last_name, Voter.c.otp, Voter.c.voted])
    with engine.connect() as conn:
        result = conn.execute(s)

        df=pd.DataFrame(result, columns=['first_name', 'last_name', 'passcode', 'voted'])

    df.voted.replace(False, "", inplace=True)

    df.to_csv(f"voter-status_{now}.csv")
    print("Done.")
