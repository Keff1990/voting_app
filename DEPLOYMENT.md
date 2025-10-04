# Deployment Guide

Follow the steps below to deploy the voting app from scratch.

## 1. Pull the Repository

```bash
git clone https://github.com/Keff1990/voting_app.git
cd voting_app
git checkout 2025_main
```

If you already have the repo, ensure it is up to date:

```bash
git fetch origin
git checkout 2025_main
git pull origin 2025_main
```

## 2. Configure Environment Variables

Create a `.env` file in the project root with the following keys:

```
FLASK_APP=autoapp.py
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
DATABASE_URL=sqlite:////absolute/path/to/voting_app/voting_app/dev.db
SEND_FILE_MAX_AGE_DEFAULT=0
```

- Adjust `DATABASE_URL` if you are using a different database backend.
- For production, set `SEND_FILE_MAX_AGE_DEFAULT` to a larger value (e.g., `31556926`).
- If a previous deployment already has a `.env`, you can reuse it—just review the values above and update paths/secrets as needed.

## 3. Install Python 3.11 (if needed)

The application targets Python 3.11. On Ubuntu/Debian-based distributions you can install it via the Deadsnakes PPA:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

Confirm the version:

```bash
python3.11 --version
```

You will use this interpreter when creating the virtual environment in the next step.

## 4. Upload Required Data Files

Place the yearly data under `yearly_upload_files/` (these files are git-ignored, so each environment must provide them):

- `db_users.csv` (columns: `last_name,first_name,otp`)
- `deacon_nominees.csv` (columns: `id,full_name`)
- `elder_nominees.csv` (columns: `id,full_name`)
- PNG headshots named `[id].png` for each nominee (optional; abstain does not require an image).

Refer to `yearly_upload_files/README.md` for formatting details.

## 5. Initialize the Database and Import Users

Activate your virtual environment (create one if needed) and install dependencies:

```bash
python3.11 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt
```

Create/migrate the database:

```bash
flask db upgrade
```

Load the yearly voter list:

```bash
python -c "from voting_app.start_database import load_users; load_users()"
```

This replaces the `voters` table with the contents of `yearly_upload_files/db_users.csv` and resets the `voted` flag.

## 6. Run the Application

For development or simple local hosting:

```bash
FLASK_APP=autoapp.py flask run --host=0.0.0.0 --port=<preferred-port>
```

For production, use a WSGI server (example with Gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:<preferred-port> autoapp:app
```

Behind a reverse proxy (Nginx/Apache), configure the proxy to forward to the chosen port.

## 7. Post-Deployment Smoke Tests

1. **Login**: Use a known voter’s credentials to confirm the login flow works and invalid combinations show appropriate errors.
2. **Voting page**: Ensure nominee lists (including "Abstain") display with correct images/names, and the form prevents empty submissions.
3. **Vote submission**: Submit ballots—both regular nominees and abstain-only—and confirm success messages appear and the voter is logged out.
4. **Database checks**: Verify the `voters` table reflects `voted=True` after submission and that `votes` rows include abstain entries when selected.
5. **Static assets**: Confirm nominee images load via the `/elections/nominee-images/<filename>` route.

## 8. Helper Utilities

Use the Python shell to inspect data:

```bash
flask shell
```

Examples:

```python
from sqlalchemy import func, select
from voting_app.extensions import db
from voting_app.vote.models import Vote, Voter

# Count votes per option
stmt = select(Vote.type, Vote.name, func.count()).group_by(Vote.type, Vote.name)
for vote_type, name, count in db.session.execute(stmt):
    print(vote_type, name, count)

# Count voters
db.session.execute(select(func.count(Voter.id))).scalar()
```

Helper scripts:

- `python -c "from voting_app.read_database import get_data; print(get_data())"` – summary of votes per nominee
- `python -c "from voting_app.read_database import get_otp; get_otp('Alice', 'Smith')"` – lookup passcodes by name
- `python -c "from voting_app.read_database import get_turnout_summary; get_turnout_summary()"` – turnout totals and percentage
- `python -c "from download_data import download_data; download_data('voting_app/dev.db')"` – export votes and voter status CSVs.

Keep the virtual environment active while running helper commands.
