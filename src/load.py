import csv
import logging.config
import os
import sqlite3
from collections.abc import Mapping, Sequence

from config.config import DATABASE, LOG_FILE_PATH, LOGGING_CONFIG_FILE

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")


def save_to_db(
        users: Sequence[Mapping]
) -> None:
    """
    Saves a sequence of user dictionaries to a database.

    Parameters
    ----------
    users (Sequence[Mapping]):
        A sequence of dictionaries representing user data.
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
    except Exception as exc:
        logger.error("Saving to database failed:", exc)
        conn.rollback()

def save_to_file(
        users: Sequence[Mapping]
) -> None:
    """
    Saves a sequence of user dictionaries to a CSV file.

    Parameters
    ----------
    users (Sequence[Mapping]):
        A sequence of dictionaries representing user data.
    """
    if not users:
        logger.error("Users sequence is empty.")
        return

    file_name = "data/file/users.csv"
    file_exists = os.path.isfile(file_name) and os.path.getsize(file_name) > 0
    file_mode = 'a' if file_exists else 'w'

    try:
        with (open(file_name, mode=file_mode, newline='', encoding="utf-8")
              as file):
            writer = csv.DictWriter(file, fieldnames=users[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(users)
    except Exception as exc:
        logger.error("Saving to file failed:", exc)

    if file_exists:
        logger.info(f"New users has been appended to {file_name}.")
    else:
        logger.info(f"{file_name} has been created with new users.")
