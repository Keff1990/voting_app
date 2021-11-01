from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import current_user, login_required, login_user, logout_user
from voting_app.extensions import login_manager
from voting_app.utils import flash_errors
from voting_app.vote.forms import (
    VotationForm,
    VoterForm,
    RequestOTPForm,
    deacons_images,
    elders_images,
)
from voting_app.vote.models import Vote, Voter

blueprint = Blueprint(
    "election", __name__, url_prefix="/elections", static_folder="../static"
)


@login_manager.user_loader
def load_user(voter_id):
    """Load user by ID."""
    return Voter.get_by_id(int(voter_id))


@blueprint.route("/", methods=["GET", "POST"])
def login():
    """Login Page."""
    form_login = VoterForm(request.form)
    form_request = RequestOTPForm(request.form)
    request_success = False
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        if form_login.submitlogin.data:
            if form_login.validate():
                # print(form_login.voter)
                login_user(form_login.voter)
                flash("You are logged in.", "success")
                redirect_url = request.args.get("next") or url_for("election.vote")
                return redirect(redirect_url)
            else:
                flash_errors(form_login)

        if form_request.submitrequest.data:
            if form_request.validate():
                # INPUT API REQUEST FOR SMS MESSAGE HERE
                flash("Your Passcode has been sent to your mobile device.", "message")
                request_success = True
            else:
                flash_errors(form_request)

    return render_template(
        "elections/login.html",
        form_login=form_login,
        form_request=form_request,
        request_success=request_success,
    )


@blueprint.route("/vote/", methods=["GET", "POST"])
@login_required
def vote():
    now = datetime.now()

    """Present vote page."""
    form = VotationForm(request.form)

    print(current_user.id)
    if form.validate_on_submit():
        if form.deacons.data:
            for deacon in form.deacons.data:
                print(current_user.id, deacon, now)
                Vote.create(
                    voter_id=current_user.id,
                    type="deacon",
                    name=deacon,  # check how to access id of deacon
                    date=now,
                )
        if form.elders.data:
            for elder in form.elders.data:
                print(current_user.id, elder, now)
                Vote.create(
                    voter_id=current_user.id,
                    type="elder",
                    name=elder,  # check how to access id of elder
                    date=now,
                )

        if (form.deacons.data) or (form.elders.data):
            current_user.update(voted=True)
            flash("Thank you for voting.", "success")
            return redirect(url_for("election.submit"))
        else:
            flash_errors(form)
    return render_template(
        "elections/vote.html",
        form=form,
        deacons_images=deacons_images,
        elders_images=elders_images,
    )


@blueprint.route("/submit/")
@login_required
def submit():
    """Logout."""
    logout_user()
    # flash("You are logged out.", "info")
    return redirect(url_for("election.submitted"))


@blueprint.route("/submitted/")
def submitted():
    return render_template("elections/submitted.html")
