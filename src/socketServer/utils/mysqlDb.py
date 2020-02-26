import pymysql

from src.socketServer.cvServer.conf.conf import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB_NAME


def createMysqlConnection():
    return pymysql.connect(host=MYSQL_HOST,
                           user=MYSQL_USERNAME,
                           passwd=MYSQL_PASSWORD,
                           db=MYSQL_DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor,
                           autocommit=True)
