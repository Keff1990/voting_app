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


def get_turnout_summary():
    """Print total voters, number who have voted, and percentage turnout."""

    Voter = vote.models.Voter

    total_stmt = select(func.count(Voter.id))
    voted_stmt = select(func.count(Voter.id)).where(Voter.voted.is_(True))

    total_voters = db.session.execute(total_stmt).scalar() or 0
    voted_voters = db.session.execute(voted_stmt).scalar() or 0

    percentage = 0
    if total_voters:
        percentage = round((voted_voters / total_voters) * 100, 2)

    print(
        f"Received {voted_voters} out of {total_voters} votes from the database. ({percentage}%)"
    )

    return {
        "total": total_voters,
        "voted": voted_voters,
        "percentage": percentage,
    }
