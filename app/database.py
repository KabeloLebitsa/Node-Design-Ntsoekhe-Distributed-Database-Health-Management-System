from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_database_connection():
    engine = create_engine('sqlite:///ntsoekhe.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session


# Uncomment if automatic database creation is desired
# def create_database():
#     engine = create_engine('sqlite:///ntsoekhe.db')
#     # Database creation logic here (if needed)
