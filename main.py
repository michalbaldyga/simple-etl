from src.extract import get_users, get_user_carts


def main():
    #r = get_users(10, 0, ['age'])
    r = get_user_carts(6)
    print(r)


if __name__ == "__main__":
    main()
