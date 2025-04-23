import os

from sqlalchemy.engine.url import URL
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.util import EMPTY_DICT

import model.database_model

database_url = URL.create(
    drivername='mysql+pymysql',
    host="127.0.0.1",
    port=3306,
    username="root",
    password=None,
    database="sistem_spk"
)

engine = create_engine(database_url, echo=True if __name__ == "__main__" else False)

def migration():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    migration()
