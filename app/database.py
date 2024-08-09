import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#export DB_CONNECTION_STRING="mysql+mysqlconnector://root:password01@localhost/APTARV8"
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password01@localhost/APTARV8" #os.environ.get('DB_CONNECTION_STRING')



engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()