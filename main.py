import logging.config

from config.config import DATABASE_PATH, LOG_FILE_PATH, LOGGING_CONFIG_FILE
from src.extract import get_users
from src.load import (
    close_db_connection,
    create_users_table,
    insert_into_users,
    open_db_connection,
)
from src.transform import get_user_data

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")


def main():
    user_params = ["firstName", "lastName", "age", "gender", "address"]
    batch_size = 1
    offset = 0
    conn = None

    while True:
        try:
            users = get_users(batch_size, offset, user_params)
            if not users:
                break

            users_clean = [get_user_data(user) for user in users]

            if not conn:
                conn = open_db_connection(DATABASE_PATH)

            create_users_table(conn)
            insert_into_users(conn, users_clean)
            offset += batch_size

        except Exception as exc:
            logger.error(f"An unexpected error occurred: {exc}")

        finally:
            close_db_connection(conn)

        break


if __name__ == "__main__":
    main()
