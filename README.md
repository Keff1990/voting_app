# Voting App – Quick Maintenance Guide

Use this guide when the Python environment and dependencies are already in place and you only need to refresh data or monitor the 2025 election run.

## 1. Pull the Latest Code (branch `2025_main`)

Run the following from the project root to ensure you have the newest templates, forms, and helpers:

```bash
git fetch origin
git checkout 2025_main
git pull origin 2025_main
```

## 2. Replace the Entire Voter List

1. Update `yearly_upload_files/db_users.csv` with the new roster (columns: `last_name,first_name,email,mobile,otp`).
2. Import the CSV, which replaces all existing voters and resets the `voted` flag:

   ```bash
   python -c "from voting_app.start_database import load_users; load_users()"
   ```

   > Uses `DATABASE_URL` from `.env`. Run from the repo root so relative paths resolve.

## 3. Add a Single Voter (without touching the rest)

Use the `create_test_user` helper when you only need to insert one entry:

```bash
python -c "from voting_app.start_database import create_test_user; create_test_user(first_name='Juan', last_name='Dela Cruz', otp='OTP1234', email='juan@example.com', mobile='09171234567', voted=False)"
```

- Omitting `db_url` makes the helper read `DATABASE_URL` from `.env`.
- Set `voted=True` only if you’re restoring a record that already cast a ballot.

## 4. Reset Votes While Keeping the Current Roster

If you are reusing the same voter list but need a clean ballot box:

```bash
flask shell
```

Then run inside the shell:

```python
from voting_app.extensions import db
from voting_app.vote.models import Vote, Voter

Vote.query.delete()                 # clears all cast ballots
Voter.query.update({Voter.voted: False})
db.session.commit()
```

This preserves voter info, empties the `votes` table, and marks everyone as not yet voted.

## 5. Check How Many Have Voted Online

```bash
python -c "from voting_app.read_database import get_turnout_summary; get_turnout_summary()"
```

The command prints total voters, ballots received, and turnout percentage.

## 6. See Vote Counts per Candidate/Nominee

Quick console view:

```bash
python -c "from voting_app.read_database import get_data; print(get_data())"
```

CSV export (also captures voter status):

```bash
python -c "from download_data import download_data; download_data('voting_app/dev.db')"
```

Two files are produced in the project root: `votes_<timestamp>.csv` (per nominee totals) and `voter-status_<timestamp>.csv`.

## 7. Verify Whether Specific Voters Have Voted

### Single voter lookup

```bash
python -c "from voting_app.read_database import get_otp; get_otp('Juan', 'Dela Cruz')"
```

- Wildcards are supported (`get_otp('%an%', 'Dela%')`) because the helper uses SQL `LIKE`.
- Output labels each match as `Already voted` or `Available` and echoes the OTP.

### Batch / multiple voters

Currently there is no one-command helper that accepts a list of names and prints only those statuses. Use the CSV created by `download_data` (see step 6) to filter or pivot the data in Excel/Sheets for any subset you need.

## Missing or Future-Nice-to-Haves

- A CLI helper that ingests a list (CSV or newline-separated names) and reports only those voters’ statuses would remove the manual filtering step described above. Let me know if you want this scripted and we can add it next.

Need another maintenance shortcut? Reach out and we can extend this guide.

## Appendix: Update Nominee Lists

1. Edit `yearly_upload_files/deacon_nominees.csv` and `yearly_upload_files/elder_nominees.csv` using the `id,full_name` columns (both files are git-ignored, so keep copies per deployment).
2. Add or replace nominee headshots in `yearly_upload_files/` with filenames that match the nominee `id` (`[id].png`).
3. Voters who submit without selecting any nominees are recorded as abstain automatically—no CSV entry is needed.
4. Changes take effect the next time the application starts.
