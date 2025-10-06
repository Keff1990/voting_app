from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask import abort

from flask_login import current_user, login_required, login_user, logout_user
from voting_app.extensions import login_manager
from voting_app.utils import flash_errors
from voting_app.vote.forms import (
    VotationForm,
    VoterForm,
    deacons_images,
    elders_images,
)
from voting_app.vote.models import Vote, Voter

blueprint = Blueprint(
    "election", __name__, url_prefix="/elections", static_folder="../static"
)

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "yearly_upload_files"


@login_manager.user_loader
def load_user(voter_id):
    """Load user by ID."""
    return Voter.get_by_id(int(voter_id))


@blueprint.route("/", methods=["GET", "POST"])
def login():
    """Login Page."""
    form_login = VoterForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST" and form_login.submitlogin.data:
        if form_login.validate():
            login_user(form_login.voter)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("election.vote")
            return redirect(redirect_url)
        flash_errors(form_login)

    return render_template(
        "elections/login.html",
        form_login=form_login,
    )


@blueprint.route("/vote/", methods=["GET", "POST"])
@login_required
def vote():
    now = datetime.now()

    """Present vote page."""
    form = VotationForm(request.form)

    print(current_user.id)
    if form.validate_on_submit():
        recorded_vote = False

        if form.deacons.data:
            for deacon in form.deacons.data:
                print(current_user.id, deacon, now)
                Vote.create(
                    voter_id=current_user.id,
                    type="deacon",
                    name=deacon,
                    date=now,
                )
                recorded_vote = True

        if form.elders.data:
            for elder in form.elders.data:
                print(current_user.id, elder, now)
                Vote.create(
                    voter_id=current_user.id,
                    type="elder",
                    name=elder,
                    date=now,
                )
                recorded_vote = True

        if not recorded_vote:
            Vote.create(
                voter_id=current_user.id,
                type="abstain",
                name="abstain",
                date=now,
            )

        current_user.update(voted=True)
        flash("Thank you for voting.", "success")
        return redirect(url_for("election.submit"))

    elif request.method == "POST":
        flash_errors(form)

    deacon_options = list(zip(list(form.deacons), deacons_images))
    elder_options = list(zip(list(form.elders), elders_images))

    return render_template(
        "elections/vote.html",
        form=form,
        deacon_options=deacon_options,
        elder_options=elder_options,
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


@blueprint.route("/nominee-images/<path:filename>")
def nominee_image(filename):
    """Serve nominee image files stored in the yearly upload directory."""

    try:
        return send_from_directory(UPLOAD_DIR, filename)
    except FileNotFoundError:
        abort(404)
