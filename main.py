from src.extract import get_users


def main():
    r = get_users(10, 0, ['age'])
    print(r)


if __name__ == "__main__":
    main()
