from src.extract import get_users, get_user_carts, get_product_category


def main():
    #r = get_users(10, 0, ['age'])
    r = get_user_carts(6)
    print(r)
    r = get_product_category(108)
    print(r)


if __name__ == "__main__":
    main()
