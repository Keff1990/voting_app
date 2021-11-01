from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import Voter

deacons_list = [
    ("philip", "Philip Blanco"),
    ("theo", "Theo Espinosa"),
    ("jourd", "Jourd Lee"),
    ("caleb", "Caleb Ramirez"),
    ("lark", "Lark Silva"),
    ("regie", "Regie Salas"),
]
elders_list = [
    ("sherwin", "Sherwin Chua"),
    ("ave", "Ave Gaspar"),
    ("rommel", "Rommel Yazon"),
]

deacons_images = [f"{x[0]}.png" for x in deacons_list]
elders_images = [f"{x[0]}.png" for x in elders_list]


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

    def validate_name(self, val1, val2):
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

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(VoterForm, self).__init__(*args, **kwargs)
        self.voter = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(VoterForm, self).validate()
        if not initial_validation:
            return False

        now = datetime.now()
        # if now < datetime(2021, 1, 17):
        #     self.otp.errors.append("Voting is still closed. Voting will open on January 17, and close at January 31, 5:00 PM.")
        #     return False
        #
        # if now > datetime(2021, 1, 31, 17, 00):
        #     self.otp.errors.append("Voting has closed. Voting closed at January 31, 5:00 PM.")
        #     return False

        self.voter = Voter.query.filter_by(otp=self.otp.data).first()
        if not self.voter:
            self.otp.errors.append("Incorrect Passcode. Please try again.")
            return False

        # print(self.voter.first_name.lower(), self.first_name.data.lower())
        if not self.validate_name(
            self.voter.first_name.replace("ñ", "n"),
            self.first_name.data.replace("ñ", "n"),
        ):
            self.first_name.errors.append(
                "Name does not match your Passcode. Please use the name in your GCF membership. Please try again."
            )
            return False

        # print(self.voter.last_name.lower(), self.last_name.data.lower())

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
    # submit = SubmitField("Submit")

    def validate(self):
        """Validate the form."""
        initial_validation = super(VotationForm, self).validate()
        if not initial_validation:
            return False

        return True
