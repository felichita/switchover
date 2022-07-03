from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from app import switchover as application

if __name__ == '__main__':
    application.run()