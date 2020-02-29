from src.socketServer.utils.redisDb import Redis
from src.socketServer.cvServer.conf.conf import REDIS_DB_NAME


class RedisForOnlineList:
    """ 封装有关课堂在线列表的数据库操作

        key format: STATUS:ONLINE_LIST:ID:(lesson_id)_(uid)
        存储的是一个uid
        这个key的用法实际上并不是很好，但是能实现需求
    """
    # 主键是由lesson_id与uid组成，中间通过下划线连接
    __PRIMARY_KEY = 'ID'
    __TABLE_NAME = 'ONLINE_LIST'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def refresh(self, lesson_id, uid):
        """ 刷新用户状态，即重置key的存活时间

        :param lesson_id: 课程下课堂唯一标识
        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:ONLINE_LIST:ID:(lesson_id)_(uid)
        key = self.__PREFIX + ':' + str(lesson_id) + '_' + str(uid)

        self.__conn.setex(name=key, value=uid, time=5)

    def getOnlineList(self, lesson_id):
        """ 获取该课堂在线的uid列表

        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        online_list = []
        key_list = self.__conn.keys(self.__PREFIX + ':' + str(lesson_id) + '_*')
        for key in key_list:
            online_list.append(self.__conn.get(key))

        return online_list
