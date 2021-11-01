"""User models."""
import datetime as dt

from flask_login import UserMixin

from voting_app.database import Column, PkModel, db, reference_col, relationship
from voting_app.extensions import bcrypt


class Voter(UserMixin, PkModel):
    """A voter."""

    __tablename__ = "voters"
    first_name = Column(db.String(30), nullable=False)
    last_name = Column(db.String(30), nullable=False)
    email = Column(db.String(20), nullable=True)
    mobile = Column(db.String(20), nullable=True)

    otp = Column(db.String(10), nullable=False)

    voted = Column(db.Boolean(), default=False)

    def __init__(self):
        pass

    def set_otp(self, otp):
        """Set password."""
        self.otp = otp

    def check_otp(self, otp):
        """Check password."""
        return otp == self.otp

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"{self.first_name} {self.last_name} voted: {self.voted}"


class Vote(PkModel):
    """A vote of the voter."""

    __tablename__ = "votes"
    voter_id = reference_col("voters", nullable=False)
    voter = relationship("Voter", backref="votes")
    type = Column(db.String(30), nullable=False)
    name = Column(db.String(30), nullable=False)
    date = Column(db.DateTime(), nullable=False)
    #
    # def __init__(self, **kwargs):
    #     self.voter_id=voter_id
    #     self.type=type
    #     self.name=name
    #     self.date=date

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"{self.voter_id} {self.type} {self.name}"
