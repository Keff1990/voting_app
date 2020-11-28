from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import Voter

deacons_list = [
    ('eliza', 'Eliza Shih-Chiusinco'),
    ('najee', 'Najee Chua'),
    ('levi', 'Levi Fabellar'),
    ('sam', 'Sam Hernando'),
    ('noel', 'Noel Mojica'),
    ('arnel', 'Arnel Nunez'),
    ('jeff', 'Jeff Tan'),
    ('rj', 'RJ Yu'),
]
elders_list = [
    ('june', 'June Acebedo'),
    ('jon', 'Jon Biscocho'),
    ('ed', 'Ed Dames'),
    ('bong', 'Bong Durana'),
    ('dan', 'Dan Guina'),
    ('aris', 'Aris Lumague'),
    ('arnold', 'Arnold Perona'),
    ('marlon', 'Marlon Roldan'),
    ('eugene', 'Eugene Villanueva'),
]

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

    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(min=2, max=30)]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(min=2, max=30)]
    )
    otp = StringField(
        "Passcode", validators=[DataRequired(), Length(min=5, max=10)]
    )

    def validate_name(self, val1, val2):
        '''validates if the name might be valid'''

        def ordered_letters(val1, val2):
            '''validates if val2 letters in val1 by order'''
            tv1 = val1
            this_name = ''
            this_i = 0
            for c2 in val2:
                this_list = []
                this_list = [(i, c1) for i, c1 in enumerate(val1[this_i:]) if c1 == c2]
                if this_list:
                    this_i = this_list[0][0]
                    this_name += c2
            if val2 == this_name: return True
            return False

        val1 = val1.lower()
        val2 = val2.lower()

        for v1, v2 in [[val1, val2], [val2, val1]]:
            if v1 == v2:
                return True
            if v2 in v1:
                return True
            if (len(v2) > 2) and (ordered_letters(v1, v2)):
                return True

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

        self.voter = Voter.query.filter_by(otp=self.otp.data).first()
        if not self.voter:
            self.otp.errors.append("Incorrect Passcode. Please try again.")
            return False

        if validate_name(self.voter.first_name, self.first_name.data):
            self.first_name.errors.append("Name does not match your Passcode. Please use the name in your GCF membership. Please try again.")
            return False

        if self.last_name.lower() != self.last_name.data.lower():
            self.last_name.errors.append("Name does not match your Passcode. Please use the name in your GCF membership. Please try again.")
            return False

        if self.voter.voted:
            self.otp.errors.append("Member has already voted. For questions, please contact GCF.")
            return False

        return True

class VotationForm(FlaskForm):
    """Votation Form."""
    elders = MultiCheckboxField("Elders", choices=elders_list)
    deacons = MultiCheckboxField("Deacons", choices=deacons_list)
    submit = SubmitField("Submit")
