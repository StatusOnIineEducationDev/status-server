from src.edu import CourseStatus, ChatStatus
from src.socketServer.utils.redisDb import Redis
from src.socketServer.cvServer.conf.conf import REDIS_DB_NAME


class RedisForLessonStatus:
    """ 封装有关课堂的各种状态的数据库操作

        key format: STATUS:LESSON_STATUS:ID:xxx
        存储的是一个map
            |- id
            |- course_status
            |- chat_status
    """
    __PRIMARY_KEY = 'ID'
    __TABLE_NAME = 'LESSON_STATUS'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def createLesson(self, lesson_id):
        """ 插入一条课堂状态记录

        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:ID:xxx
        key = self.__PREFIX + ':' + lesson_id
        record_dict = {
            'lesson_id': lesson_id,
            'course_status': CourseStatus.Waiting,
            'chat_status': ChatStatus.Free
        }
        self.__conn.hset(key, record_dict)


class RedisForInLesson:
    """ 封装有关用户上课情况的数据库操作

        key format: STATUS:IN_LESSON:UID:xxx
        存储的是一个map
            |- uid
            |- course_id
            |- lesson_id
    """
    __PRIMARY_KEY = 'UID'
    __TABLE_NAME = 'IN_LESSON'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def joinLesson(self, uid, course_id, lesson_id):
        """ 插入一条用户上课记录

            当用户退出该课堂的话
            需要删除该条记录
        :param uid: 用户唯一标识
        :param course_id: 课程唯一标识
        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__PREFIX + ':' + uid
        record_dict = {
            'uid': uid,
            'course_id': course_id,
            'lesson_id': lesson_id
        }
        self.__conn.hset(key, record_dict)

    def quitLesson(self, uid):
        """ 用户退出当前课堂

            把该key删除
        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__PREFIX + ':' + uid
        self.__conn.delete(key)

    def isInLesson(self, uid):
        """ 查询用户是否在上课

        :param uid: 用户唯一标识
        :return: True - 在课室中/正在上课（即Waiting或Online状态）
                 False - 空闲状态
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__PREFIX + ':' + uid

        return self.__conn.hexists(key)

    def getLessonID(self, uid):
        """ 获取该用户当前课堂的id

        :param uid: 用户唯一标识
        :return: id - 存在（在课室中/正在上课）
                 None - 不存在（空闲状态）
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__PREFIX + ':' + uid

        return self.__conn.hget(key, 'lesson_id')
