from src.extract import get_user_carts, get_users
from src.transform import (
    extract_products_from_carts,
    group_products_by_category, get_most_common_category,
)


def main():
    user_params = ["firstName", "lastName", "age", "gender", "address"]
    users = get_users(1, 5, user_params)
    carts = get_user_carts(6).get('carts')
    carts = [carts[0], carts[0]]
    # r = get_product_category(108)
    print(users)
    print(carts)

    products = extract_products_from_carts(carts)
    products_gr = group_products_by_category(products)
    products_gr['test'] = 20
    print(products_gr)
    print(get_most_common_category(products_gr))
    # get_user_country(52.509669, 13.376294)

if __name__ == "__main__":
    main()
