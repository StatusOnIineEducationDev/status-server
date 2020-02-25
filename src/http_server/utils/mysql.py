import pymysql

from src.http_server.config.conf import *


def getDatabaseConnection():
    return pymysql.connect(host=SQL_HOST,
                           user=USERNAME,
                           passwd=PASSWORD,
                           db=DATABASE,
                           cursorclass=pymysql.cursors.DictCursor,
                           autocommit=True)
