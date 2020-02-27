from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.socketServer.cvServer.conf.conf import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB_NAME


Base = declarative_base()
engine = create_engine('mysql+pymysql://' +
                       MYSQL_USERNAME + ':' +
                       MYSQL_PASSWORD + '@' +
                       MYSQL_HOST + '/' +
                       MYSQL_DB_NAME,
                       pool_size=8,
                       pool_recycle=60*30)


def getMySQLSession():
    db_session = sessionmaker(bind=engine)

    return db_session()
