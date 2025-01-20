from src.extract import get_users
from src.transform import get_user_data


def main():
    user_params = ["firstName", "lastName", "age", "gender", "address"]
    users = get_users(10, 0, user_params).get('users')
    for user in users:
        print(get_user_data(user))

if __name__ == "__main__":
    main()
