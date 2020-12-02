import sqlalchemy as sqla
import csv
from environs import Env
import pandas as pd
from sqlalchemy import func

from voting_app import commands, vote

def get_data():
    Voter = vote.models.Voter
    Vote = vote.models.Vote

    df = pd.DataFrame(Vote.query.with_entities(Vote.type, Vote.name, func.count(Vote.id))\
            .group_by(Vote.type, Vote.name).all(), columns=['type', 'name', 'count'])

    return df
