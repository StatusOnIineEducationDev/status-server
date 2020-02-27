from src.edu import UserStatus
from src.socketServer.utils.redisDb import Redis
from src.socketServer.cvServer.conf.conf import REDIS_DB_NAME


class RedisForUserStatus:
    """ 封装有关用户的各种状态的数据库操作

        key format: STATUS:USER_STATUS:UID:xxx
        存储的是一个值UserStatus（参考edu.py）
    """
    __PRIMARY_KEY = 'UID'
    __TABLE_NAME = 'USER_STATUS'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def signUp(self, uid):
        """ 用户注册

        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:USER_STATUS:UID:xxx
        key = self.__PREFIX + ':' + str(uid)
        self.__conn.set(key, UserStatus.Free)

    def getUserStatus(self, uid):
        """ 获取当前课程状态

        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:USER_STATUS:UID:xxx
        key = self.__PREFIX + ':' + str(uid)
        if not self.__conn.exists(key):
            self.signUp(uid=uid)

        return int(self.__conn.get(key))

    def free(self, uid):
        """ 空闲

        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:User_STATUS:UID:xxx
        key = self.__PREFIX + ':' + str(uid)
        self.__conn.set(key, UserStatus.Free)

    def inRoom(self, uid):
        """ 在房间中

        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__PREFIX + ':' + str(uid)
        self.__conn.set(key, UserStatus.InRoom)

    def inClass(self, uid):
        """ 在课堂中

        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__PREFIX + ':' + str(uid)
        self.__conn.set(key, UserStatus.InClass)


