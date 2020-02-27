import redis

from src.socketServer.cvServer.conf.conf import REDIS_HOST, REDIS_PORT


class Redis:
    """ redis单例
        不论创建多少个Redis实例，都会共用一个连接池pool

        Example：
            Redis().conn

            实例化Redis后，通过conn对数据库进行操作
            注意Redis后的括号不能漏
            因为每一条连接都隶属一个对象，单是类名并不是一个对象
    """
    __pool = None

    def __init__(self):
        if Redis.__pool is None:
            Redis.createConnectionPool()
        self.conn = redis.Redis(connection_pool=Redis.__pool, decode_responses=True)

    @staticmethod
    def createConnectionPool():
        Redis.__pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
