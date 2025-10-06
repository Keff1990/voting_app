# Yearly Upload Files

This directory stores annual membership data used to populate the voting database.

## `db_users.csv`

- Columns (in order):
  1. `last_name` – Member's last name (text)
  2. `first_name` – Member's first name (text)
  3. `otp` – Voting passcode provided to the member (text, required, unique per voter)
- Include the header row exactly as listed above.
- Encoding should be UTF-8, with values separated by commas.

### Sample Row

```
last_name,first_name,otp
Arboleda,Makram,5XQH8J4
```

After updating the file, load it into the database by running from the project root:

```bash
python -c 'from voting_app.start_database import load_users; load_users()'
```

The importer will backfill blank `email` and `mobile` columns when it loads the table so the schema remains consistent.

## `deacon_nominees.csv` and `elder_nominees.csv`

- Columns (in order):
  1. `id` – Short, URL-friendly identifier for the nominee (also used as the image filename)
  2. `full_name` – Name displayed to voters
- Keep the header row and provide one row per nominee.
- The application reads these files on startup to populate the ballot choices.
- A voter who submits without selecting any nominees is counted as abstaining automatically; no CSV row is required.

### Sample Rows

```
id,full_name
philip,Philip Blanco
theo,Theo Espinosa
```

## Nominee Images

- Store PNG files in this directory and name each file `[id].png`, matching the `id` column from the nominees CSVs (e.g., `philip.png`).
- The voting page automatically links images to nominees using this naming convention.

> **Note:** Only `.gitkeep` and this README are tracked in version control. The CSV uploads (`db_users.csv`, `deacon_nominees.csv`, `elder_nominees.csv`) and PNG assets are intentionally git-ignored, so provide fresh copies in each environment before running the app.
