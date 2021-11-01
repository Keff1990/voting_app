import csv

import pandas as pd
import sqlalchemy as sqla
from sqlalchemy import func

from environs import Env
from voting_app import commands, vote


def get_data():
    Voter = vote.models.Voter
    Vote = vote.models.Vote

    df = pd.DataFrame(
        Vote.query.with_entities(Vote.type, Vote.name, func.count(Vote.id))
        .group_by(Vote.type, Vote.name)
        .all(),
        columns=["type", "name", "count"],
    )

    return df


def get_otp(fname, lname):
    Voter = vote.models.Voter

    results = (
        Voter.query.filter(Voter.first_name.like(fname), Voter.last_name.like(lname))
        .with_entities(Voter.first_name, Voter.last_name, Voter.otp, Voter.voted)
        .all()
    )

    for r in results:
        if r[3]:
            voted = "Already voted"
        else:
            voted = "Available"
        print(f"{voted}. {r[0]} {r[1]}. OTP: {r[2]}")
