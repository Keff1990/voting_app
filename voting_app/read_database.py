import pandas as pd
from sqlalchemy import func, select

from voting_app import vote
from voting_app.extensions import db


def get_data():
    Voter = vote.models.Voter
    Vote = vote.models.Vote

    stmt = (
        select(Vote.type, Vote.name, func.count(Vote.id))
        .group_by(Vote.type, Vote.name)
    )
    results = db.session.execute(stmt).all()

    df = pd.DataFrame(results, columns=["type", "name", "count"])

    return df


def get_otp(fname, lname):
    Voter = vote.models.Voter

    stmt = (
        select(Voter.first_name, Voter.last_name, Voter.otp, Voter.voted)
        .where(Voter.first_name.like(fname), Voter.last_name.like(lname))
    )
    results = db.session.execute(stmt).all()

    for r in results:
        if r[3]:
            voted = "Already voted"
        else:
            voted = "Available"
        print(f"{voted}. {r[0]} {r[1]}. OTP: {r[2]}")
