[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ManassehV2_aptarapi&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ManassehV2_aptarapi)
### Note on Database Migrations and Tests
In the `main.py` file, there is a line related to database schema creation:

```python
# models.Base.metadata.create_all(bind=engine)
'''
This line has been commented out to bypass a pytest error when running the tests in GitHub Actions.
If you are running the application locally or with docker-compose and need to create the database schema, uncomment this line in main.py:
'''python
models.Base.metadata.create_all(bind=engine)
'''
This will ensure that the database tables are created when the application starts. 

## Running the Application with Docker

### step 1: Setup Environment Variables

Before running the project, you need to set up the environment variables. This is done by creating a `.env` file in the root directory of this project.

### Steps to Create `.env` File

1. In the root directory of the project, create a file named `.env`.
2. Add the following content to the `.env` file:

   ```env
   MYSQL_ROOT_PASSWORD=password01
   MYSQL_DATABASE=aptardb
   DATABASE_CONNECTION_STRING=mysql+mysqlconnector://root:password01@mysql_db:3306/aptardb
   ```

3. Save the file.

These environment variables are required for connecting to the MySQL database used in the project.

- `MYSQL_ROOT_PASSWORD`: Specifies the root password for the MySQL server.
- `MYSQL_DATABASE`: The name of the MySQL database to be used.
- `DATABASE_CONNECTION_STRING`: This is the connection string used by the application to connect to the MySQL database.

### Step 2: Build and Run the Containers

Use Docker Compose to build and run the containers. This will set up the FastAPI app, a Redis instance, a Celery worker, and the Flower monitoring tool.

`docker-compose up --build`

### Step 3: Accessing the Application and Services

1. FastAPI Application: Access the API at `http://localhost:8000`.
2. Swagger Documentation: The API's documentation page can be accessed at `http://localhost:8000/docs`.
3. Flower Monitoring Tool: Access Flower at `http://localhost:5555` to monitor Celery tasks.

### Step 4: Stopping the Containers

To stop the running containers, use:

`docker-compose down`

## Running the Project Locally

### Step 1: Creating a Virtual Environment

Begin by cloning the repository to your local machine, navigating into the project directory, and creating a virtual environment:

`git clone https://github.com/ManassehV2/aptarapi.git`

`cd project-name`

`python3 -m venv aptarapivenv`

### Step 2: Activate the Virtual Environment

Activate the virtual enviroment using the following command:

`source ./aptarapivenv/bin/activate`

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
