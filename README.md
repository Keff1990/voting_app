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
1. To add users, place the provided csv in ./voting_app
1. Enter the inner voting_app folder  
`cd voting_app`
1. Run the following code:  
`python -c 'from start_database import load_users;load_users()'`

## Deployment:
1. Review the .env file provided. 
1. It is recommended to use a service such as gunicorn or nginx.
1. If none, at the root folder, run  
`flask run`

## Downloading the data
1. At the root folder, run  
`python -c 'from download_data import download_data; download_data("FILEPATH OF DATABASE")'`  
ex. `python -c 'from download_data import download_data; download_data("voting_app/dev.db")'`
