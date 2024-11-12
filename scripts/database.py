import pymysql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Connect to the database using PyMySQL
try:
    mydb = pymysql.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    )
    print("Connection successful!")

except pymysql.MySQLError as err:
    print(f"Error: {err}")
