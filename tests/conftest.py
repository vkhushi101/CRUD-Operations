import os

import pymysql
import pytest
from dotenv import load_dotenv
from src.app import app

# Load environment variables from .env file
load_dotenv()

# Retrieve the environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


@pytest.fixture
def client():
    """
    Configures the Flask application for testing mode.
    The client simulates sending HTTP requests to the Flask application and receiving responses.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def get_db_connection():
    """Return a connection to the MySQL database"""
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
    )


@pytest.fixture(scope="function", autouse=True)
def clear_storage_table():
    """Helper function to delete all entries in the storage table."""

    print("Cleaning table STORAGE")
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM storage")
        connection.commit()
    connection.close()
    yield
