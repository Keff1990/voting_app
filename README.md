# Voting App – Alpine Maintenance Playbook

Use these recipes when the Python environment is already installed on the Alpine Linux host and you just need to update data or monitor the 2025 election run.

> **DNS reminder:** Some Alpine images lose name resolution between shells. If `git fetch` or other network commands cannot reach GitHub, run `echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf` in the shell you are using, then retry. Repeat whenever you start a new session that needs outbound access.

## Use Case 1 – Update the app via `git pull` and restart `rc-service`

1. `source env/bin/activate`
2. If DNS errors appear, such as failed to connect to github, run `echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf`.
3. Pull the latest branch:
   ```bash
   git fetch origin
   git checkout 2025_main
   git pull origin 2025_main
   ```
4. Restart the system service so the code reloads:
   ```bash
   sudo rc-service voteapp restart
   ```

## Use Case 2 – Replace the entire voter list

1. `source env/bin/activate`
2. If you had to pull fresh CSVs over the network and DNS failed, re‑apply the nameserver command from the reminder above.
3. Update `yearly_upload_files/db_users.csv` with the new roster (`last_name,first_name,email,mobile,otp`).
4. Re-import voters (table is replaced and every `voted` flag resets; existing `votes` rows are cleared by default):
   ```bash
   python -c "from voting_app.start_database import load_users; load_users(reset_votes=True)"
   ```
   - Pass `reset_votes=False` if you need to preserve the `votes` table.
5. `sudo rc-service voteapp restart` to make sure the app reads the refreshed table.

## Use Case 3 – Add or edit a single voter record

1. `source env/bin/activate`
2. Insert the voter:
   ```bash
   python -c "from voting_app.start_database import create_test_user; create_test_user(first_name='Juan', last_name='Dela Cruz', otp='OTP1234', email='juan@example.com', mobile='09171234567', voted=False)"
   ```
   - Omit `db_url` to reuse `DATABASE_URL` from `.env`.
   - Set `voted=True` only when restoring someone who already cast a ballot.

## Use Case 4 – Keep the roster but reset every vote

1. `source env/bin/activate`
2. One-liner reset:
   ```bash
   python -c "from voting_app.extensions import db; from voting_app.vote.models import Vote, Voter; Vote.query.delete(); Voter.query.update({Voter.voted: False}); db.session.commit()"
   ```
3. `sudo rc-service voteapp restart` so fresh sessions can begin voting.

## Use Case 5 – Check total turnout

1. `source env/bin/activate`
2. Run:
   ```bash
   python -c "from voting_app.read_database import get_turnout_summary; get_turnout_summary()"
   ```
   Output shows total voters, those who already voted, and the percentage.

## Use Case 6 – Review votes per candidate / export CSVs

1. `source env/bin/activate`
2. Console snapshot:
   ```bash
   python -c "from voting_app.read_database import get_data; print(get_data())"
   ```
3. Full CSV export (includes voter status sheet):
   ```bash
   python -c "from download_data import download_data; download_data('dev.db')"
   ```
   This creates `votes_<timestamp>.csv` and `voter-status_<timestamp>.csv` in the repo root.

## Use Case 7 – Validate voter status (single or batch)

1. `source env/bin/activate`
2. Single lookup:
   ```bash
   python -c "from voting_app.read_database import get_otp; get_otp('Juan', 'Dela Cruz')"
   ```
   - Supports SQL wildcards, e.g., `get_otp('%an%', 'Dela%')`.
   - Prints `Already voted` or `Available` plus the OTP.
3. Batch review: Use `voter-status_<timestamp>.csv` from Use Case 6 and filter it in Excel/Sheets for the subset you care about.

## Use Case 8 – Update nominee lists and headshots

1. `source env/bin/activate`
2. Edit `yearly_upload_files/deacon_nominees.csv` and `yearly_upload_files/elder_nominees.csv` (columns: `id,full_name`). Keep backups because these files are git-ignored.
3. Drop/update headshots in `yearly_upload_files/` using `[id].png` filenames.
4. No CSV entry is needed for abstain—blank submissions are counted automatically.
5. `sudo rc-service voteapp restart` so the refreshed nominees load.


