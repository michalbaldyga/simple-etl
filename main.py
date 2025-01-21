import logging.config

from config.config import LOG_FILE_PATH, LOGGING_CONFIG_FILE
from src.extract import get_users
from src.load import save_to_db, save_to_file
from src.transform import get_user_data

logging.config.fileConfig(
    fname=LOGGING_CONFIG_FILE,
    defaults={"logfilename": repr(LOG_FILE_PATH)}
)
logger = logging.getLogger("logger_file")


def main():
    user_params = ["firstName", "lastName", "age", "gender", "address"]
    batch_size = 2
    offset = 0

    while True:
        try:
            users = get_users(batch_size, offset, user_params)
            if not users:
                break
            results = [get_user_data(user) for user in users]
            save_to_file(results)
            save_to_db(results)
            offset += batch_size
        except Exception as exc:
            logger.error(f"An unexpected error occurred: {exc}")


if __name__ == "__main__":
    main()
