# Voting App

A simple voting app made for GCF.

## Installing Packages
1. Make sure the server has python v3.+ and pip installed.
1. It is recommended to create and run python on a virtual environment.
1. Install necessary packages:  
`pip install -r requirements/dev.txt`

## To initialize a local SQLite DB:
1. On the root folder, run  
`flask db init`  
`flask db migrate`  
`flask db upgrade`  

## Adding Users:
1. Place the provided CSV inside `./yearly_upload_files` and ensure it is named `db_users.csv` (this file is git-ignored so each deployment supplies its own data).
1. From the project root, run:  
`python -c 'from voting_app.start_database import load_users; load_users()'`

## Updating Nominee Lists:
1. Edit `yearly_upload_files/deacon_nominees.csv` and `yearly_upload_files/elder_nominees.csv` using the `id,full_name` columns (both files are git-ignored, so keep copies per deployment).
1. Add or replace nominee headshots in `yearly_upload_files/` with filenames that match the nominee `id` (`[id].png`).
1. The application automatically adds an "Abstain" option for each ballot—no CSV entry is needed for it.
1. Changes take effect the next time the application starts.

## Deployment:
1. Review the .env file provided.
1. It is recommended to use a service such as gunicorn or nginx.
1. If none, at the root folder, run  
`flask run`

## Downloading the data
1. At the root folder, run  
`python -c 'from download_data import download_data; download_data("FILEPATH OF DATABASE")'`  
ex. `python -c 'from download_data import download_data; download_data("voting_app/dev.db")'`
