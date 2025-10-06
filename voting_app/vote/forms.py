import csv
from datetime import datetime
from pathlib import Path

from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import SelectMultipleField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired

from voting_app.extensions import db

from .models import Voter

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "yearly_upload_files"


def _load_nominees(csv_name):
    """Load nominee choices from CSV returning (choices, image_filenames)."""

    csv_path = UPLOAD_DIR / csv_name
    if not csv_path.exists():
        raise RuntimeError(
            f"Missing nominee CSV '{csv_name}'. Upload the file to {UPLOAD_DIR.as_posix()} before starting the app."
        )

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"id", "full_name"}
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Nominee CSV '{csv_name}' is missing required column(s): {', '.join(sorted(missing))}."
            )

        choices = []
        image_names = []
        for row in reader:
            nominee_id = (row.get("id") or "").strip()
            full_name = (row.get("full_name") or "").strip()
            if not nominee_id or not full_name:
                continue
            choices.append((nominee_id, full_name))
            image_file = f"{nominee_id}.png"
            if (UPLOAD_DIR / image_file).exists():
                image_names.append(image_file)
            else:
                image_names.append(None)

    if not choices:
        raise ValueError(
            f"Nominee CSV '{csv_name}' does not contain any rows. Please populate it before running the app."
        )

    return choices, image_names


deacons_list, deacons_images = _load_nominees("deacon_nominees.csv")
elders_list, elders_images = _load_nominees("elder_nominees.csv")

def validate_name(val1, val2):
    """validates if the name might be valid"""

    def ordered_letters(val1, val2):
        """validates if val2 letters in val1 by order"""
        tv1 = val1
        this_name = ""
        this_i = 0
        for c2 in val2:
            this_list = []
            this_list = [(i, c1) for i, c1 in enumerate(val1[this_i:]) if c1 == c2]
            if this_list:
                this_i = this_list[0][0]
                this_name += c2
        if val2 == this_name:
            return True
        return False

    val1 = val1.lower()
    val2 = val2.lower()

    print(val1, val2)

    for v1, v2 in [[val1, val2], [val2, val1]]:
        if v1 == v2:
            return True
        if v2 in v1:
            return True
        if (len(v2) > 2) and (ordered_letters(v1, v2)):
            return True
    print("fail")
    return False


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class VoterForm(FlaskForm):
    """Voter form."""

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    otp = StringField("Passcode", validators=[DataRequired()])
    submitlogin = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(VoterForm, self).__init__(*args, **kwargs)
        self.voter = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(VoterForm, self).validate(
            extra_validators=extra_validators
        )
        if not initial_validation:
            return False

        now = datetime.now()
        # if now < datetime(2021, 11, 7):
        #     self.otp.errors.append("Voting is still closed. Voting will open on January 17, and close at January 31, 5:00 PM.")
        #     return False
        #
        # if now > datetime(2021, 11, 29):
        #     self.otp.errors.append("Voting has closed. Voting closed at January 31, 5:00 PM.")
        #     return False

        stmt = select(Voter).filter_by(otp=self.otp.data)
        self.voter = db.session.execute(stmt).scalar_one_or_none()
        if not self.voter:
            self.otp.errors.append("Incorrect Passcode. Please try again.")
            return False

        if not validate_name(
            self.voter.first_name.replace("ñ", "n"),
            self.first_name.data.replace("ñ", "n"),
        ):
            self.first_name.errors.append(
                "Name does not match your Passcode. Please use the name in your GCF membership. Please try again."
            )
            return False

        if self.voter.last_name.lower().replace(
            "ñ", "n"
        ) != self.last_name.data.lower().replace("ñ", "n"):
            self.last_name.errors.append(
                "Name does not match your Passcode. Please use the name in your GCF membership. Please try again."
            )
            return False

        if self.voter.voted:
            self.otp.errors.append(
                "Member has already voted. For questions, please contact GCF."
            )
            return False

        return True


class VotationForm(FlaskForm):
    """Votation Form."""

    elders = MultiCheckboxField("Elders", choices=elders_list)
    deacons = MultiCheckboxField("Deacons", choices=deacons_list)
