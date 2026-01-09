import secrets

def main():
    # Prints a safe API key you can paste into .env
    print(secrets.token_urlsafe(32))

if __name__ == "__main__":
    main()
