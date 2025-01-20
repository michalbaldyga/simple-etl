from src.extract import get_user_carts, get_users, get_user_country
from src.transform import (
    extract_products_from_carts,
    group_products_by_category, get_most_common_category, get_user_data,
)


def main():
    user_params = ["firstName", "lastName", "age", "gender", "address"]
    users = get_users(10, 0, user_params).get('users')
    for user in users:
        print(get_user_data(user))

if __name__ == "__main__":
    main()
