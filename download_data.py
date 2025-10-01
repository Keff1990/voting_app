from datetime import datetime

import pandas as pd
import sqlalchemy as sqla
from sqlalchemy import func, select

def download_data(db_url):

    now = datetime.now().strftime('%Y-%m-%d-%H-%M')
    db_url = "sqlite:///" + db_url
    engine = sqla.create_engine(db_url, echo=True)

    metadata = sqla.MetaData()
    metadata.reflect(bind=engine)

    Vote = metadata.tables['votes']
    Voter = metadata.tables['voters']

    stmt_votes = select(Vote.c.type, Vote.c.name, func.count(Vote.c.name)).group_by(
        Vote.c.name
    )
    with engine.connect() as conn:
        vote_rows = conn.execute(stmt_votes).all()

    df = pd.DataFrame(vote_rows, columns=['type', 'name', 'votes'])

    df.to_csv(f"votes_{now}.csv")

    stmt_voters = select(
        Voter.c.first_name, Voter.c.last_name, Voter.c.otp, Voter.c.voted
    )
    with engine.connect() as conn:
        voter_rows = conn.execute(stmt_voters).all()

    df = pd.DataFrame(
        voter_rows, columns=['first_name', 'last_name', 'passcode', 'voted']
    )

    df.voted.replace(False, "", inplace=True)

    df.to_csv(f"voter-status_{now}.csv")
    print("Done.")
