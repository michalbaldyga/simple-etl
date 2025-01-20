import csv
import logging.config
import os
import sqlite3
from collections.abc import Sequence

from config.config import DATABASE

log_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")
)
logging.config.fileConfig(
    "config/logging.conf",
    defaults={"logfilename": repr(log_file_path)}
)
logger = logging.getLogger("logger_file")


def save_to_db(users: Sequence[dict]):
    """
    Saves a sequence of user dictionaries to a database.

    Parameters
    ----------
    users (Sequence[dict]):
        A sequence of dictionaries representing user data.

    Raises
    ------
    sqlite3.OperationalError
        If database operation failed.
    """
    create_table = """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, 
            first_name TEXT NOT NULL, 
            last_name TEXT NOT NULL, 
            age INT NOT NULL, 
            gender TEXT NOT NULL, 
            country TEXT, 
            fave_category TEXT
        );
    """

    insert_into = """
        INSERT INTO users(
            first_name, last_name, age, gender, country, fave_category)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    insert_values = [tuple(user.values()) for user in users]

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)

            if insert_values:
                cursor.executemany(insert_into, insert_values)

            conn.commit()
            logger.info("Database has been updated.")

    except sqlite3.OperationalError as err:
        logger.error("Database operation failed:", err)
        conn.rollback()


def save_to_file(
        users: Sequence[dict]
) -> None:
    """
    Saves a sequence of user dictionaries to a CSV file.

    Parameters
    ----------
    users (Sequence[dict]):
        A sequence of dictionaries representing user data.

    Raises
    ------
    ValueError
        If the `users` sequence is empty.
    """
    file_name = "data/file/users.csv"
    file_exists = os.path.isfile(file_name) and os.path.getsize(file_name) > 0
    file_mode = 'a' if file_exists else 'w'

    try:
        with (open(file_name, mode=file_mode, newline='', encoding='utf-8')
              as file):
            writer = csv.DictWriter(file, fieldnames=users[0].keys())

            if not file_exists:
                writer.writeheader()

            writer.writerows(users)
    except IndexError:
        logger.error("Users sequence is empty.")
        return

    if file_exists:
        logger.info(f"New users has been appended to {file_name}.")
    else:
        logger.info(f"{file_name} has been created with new users.")
