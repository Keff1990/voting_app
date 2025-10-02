# Yearly Upload Files

This directory stores annual membership data used to populate the voting database.

## `db_users.csv` format

- Columns (in order):
  1. `last_name` – Member's last name (text)
  2. `first_name` – Member's first name (text)
  3. `otp` – Voting passcode provided to the member (text, required, unique per voter)

- File must include the header row exactly as listed above.
- Encoding should be UTF-8, with values separated by commas.

### Sample Row

```
last_name,first_name,otp
Arboleda,Makram,5XQH8J4
```

## Usage

1. Replace `db_users.csv` with the current year's data using the structure above.
2. From the project root run:
   ```bash
   python -c 'from voting_app.start_database import load_users; load_users()'
   ```
   The script reads this CSV and repopulates the `voters` table.
   (Email and mobile columns are optional; if omitted they are stored as blank values.)

> **Note:** All files in this directory are ignored by git except `.gitkeep` and this README, so uploaded CSVs remain local.
