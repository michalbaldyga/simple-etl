import csv
import logging.config
import sqlite3
from collections.abc import Mapping, Sequence
from pathlib import Path
from sqlite3 import Connection, Error
from typing import Any

from config.config import (
    CSV_FILE_PATH,
    DATABASE_PATH,
    LOG_FILE_PATH,
    LOGGING_CONFIG_FILE,
)

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")


def open_db_connection(
        database: str = DATABASE_PATH
) -> Connection:
    """
    Open a connection to the SQLite database file database.

    Parameters
    ----------
    database : str
        The database file path.

    Returns
    -------
    Connection
        A connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(database)
    except Error as err:
        logger.error(f"Error occurred while attempting to "
              f"open database connection: {err}")
        raise
    return conn


def close_db_connection(
        conn: Connection | None
) -> None:
    """
    Close the database connection.

    Parameters
    ----------
    conn : Connection
        A connection to the SQLite database.
    """
    if not conn:
        return

    try:
        conn.close()
    except Error as err:
        logger.error(f"Error occurred while attempting to "
              f"close database connection: {err}")
        raise


def create_users_table(
        conn: Connection
) -> None:
    """
    Create users table in the SQLite database.

    Parameters
    ----------
    conn : Connection
        A connection to the SQLite database.
    """
    create_query_path = Path("src/sql/create_table.sql")
    try:
        create_query = create_query_path.read_text()
    except Exception as err:
        logger.error(f"Failed to read SQL file: {create_query_path} - {err}")
        raise

    try:
        cursor = conn.cursor()
        cursor.execute(create_query)
        conn.commit()
    except sqlite3.DatabaseError as err:
        logger.error("Database operation failed:", err)
        raise
    logger.info("Users table has been created.")


def insert_into_users(
        conn: Connection,
        users: Sequence[Mapping[str, Any]]
) -> None:
    """
    Insert users into SQLite database.

    Parameters
    ----------
    conn : Connection
        A connection to the SQLite database.
    users : Sequence[Mapping[str, Any]]
        A sequence of dictionaries representing user data.
    """
    if not users:
        logger.info("No users to insert.")
        return

    insert_query_path = Path("src/sql/insert_into.sql")
    try:
        insert_query = insert_query_path.read_text()
    except Exception as err:
        logger.error(f"Failed to read SQL file: {insert_query_path} - {err}")
        raise

    insert_values = [tuple(user.values()) for user in users]
    try:
        cursor = conn.cursor()
        cursor.executemany(insert_query, insert_values)
        conn.commit()
    except sqlite3.DatabaseError as err:
        logger.error("Database operation failed: %s", err)
        conn.rollback()
        raise
    logger.info("Users have been added to the database.")


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
        raise

    logger.info(f"File \"{file_path.name}\" has been updated.")
