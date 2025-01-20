import csv
import logging.config
import os
from collections.abc import Sequence

log_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")
)
logging.config.fileConfig(
    "config/logging.conf",
    defaults={"logfilename": repr(log_file_path)}
)
logger = logging.getLogger("logger_file")


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
