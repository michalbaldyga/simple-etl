from src.extract import get_users
from src.load import save_to_db
from src.transform import get_user_data


def main():
    user_params = ["firstName", "lastName", "age", "gender", "address"]
    users = get_users(2, 0, user_params).get('users')
    results = []
    for user in users:
        results.append(get_user_data(user))

    save_to_db(results)


if __name__ == "__main__":
    main()
