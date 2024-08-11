[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi)

# Project Setup Instructions

This document outlines the steps required to set up and run the application. All commands needs to be executed from the root directiory of the project!!

## Setting up the Environment

### Step 1: Creating a Virtual Environment

To avoid dependency conflicts, it is recommended to create a virtual environment. You can do this using the following command:

`python3 -m venv aptarapivenv`

### Step 2: Activate the Virtual Environment

Activate the virtual enviroment using the following command:

`
source ./aptarapivenv/bin/activate
`

### Step 3: Install required dependencies

Now install the dependencies from the requirements.txt file using the following command

`pip install -r requirements.txt`

### Step 4: Export the database connection string

To connect your application to the database, export the connection string as an environment variable:

`export DB_CONNECTION_STRING="mysql+mysqlconnector://user:password@server/dbname"`

**Replace:**

- `user`: Your database username.
- `password`: Your database password.
- `server`: The database server's hostname or IP.
- `dbname`: The name of your database.

**Verify:**

Run `echo $DB_CONNECTION_STRING` to ensure it’s set correctly.

### Step 5: Initialize the Database

If you are running the app for the first time, uncomment the following line in main.py to create the database schema:

`#models.Base.metadata.create_all(bind=engine)`

This will initialize the database tables. Once the database is set up, you can comment this line out again to prevent re-creating the tables on subsequent runs.

### Step 6: Run the Application

Now, once you have the enviromenment prepared, you can run the application, from the root diroctory, with:

`fastapi dev  app/main.py`

### Step 7: Accessing the API's swagger doc page

Once you have the application up and running, the API's docmentation page(swagger) can be accessed at http://127.0.0.1:8000/docs/ where you can send your requests to the app post end point
