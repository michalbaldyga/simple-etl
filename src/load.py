import csv
import logging.config
import sqlite3
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from config.config import (
    DATABASE_PATH,
    LOG_FILE_PATH,
    LOGGING_CONFIG_FILE,
)

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")


def save_to_db(
        users: Sequence[Mapping[str, Any]]
) -> None:
    """
    Save a sequence of user dictionaries to a database.

    Parameters
    ----------
    users : Sequence[Mapping[str, Any]]
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
        with sqlite3.connect(DATABASE_PATH) as conn:
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
        users: Sequence[Mapping[str, Any]]
) -> None:
    """
    Save a sequence of user dictionaries to a CSV file.

    Parameters
    ----------
    users : Sequence[Mapping[str, Any]]
        A sequence of dictionaries representing user data.
    """
    if not users:
        logger.error("Users sequence is empty.")
        return

    CSV_FILE_PATH = "data/file/users.csv"
    file_path = Path(CSV_FILE_PATH)
    file_exists = file_path.exists()
    file_mode = 'a' if file_exists else 'w'

    try:
        with file_path.open(mode=file_mode, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=users[0].keys())

            if not file_exists:
                writer.writeheader()

            writer.writerows(users)

    except Exception as exc:
        logger.error("Saving to file failed:", exc)

    logger.info(f"File \"{file_path.name}\" has been updated.")
