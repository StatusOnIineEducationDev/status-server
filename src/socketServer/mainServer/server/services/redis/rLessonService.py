from src.edu import CourseStatus, ChatStatus
from src.socketServer.utils.redisDb import Redis
from src.socketServer.cvServer.conf.conf import REDIS_DB_NAME


class RedisForLessonStatus:
    """ 封装有关课堂的各种状态的数据库操作

        key format: STATUS:LESSON_STATUS:LESSON_ID:xxx
        存储的是一个map
            |- lesson_id
            |- chat_status
    """
    __PRIMARY_KEY = 'LESSON_ID'
    __TABLE_NAME = 'LESSON_STATUS'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def createLesson(self, lesson_id):
        """ 插入一条课堂状态记录

        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:LESSON_ID:xxx
        key = self.__PREFIX + ':' + str(lesson_id)
        record_data = {
            'lesson_id': lesson_id,
            'course_status': CourseStatus.Waiting,
            'chat_status': ChatStatus.Free
        }
        self.__conn.hmset(key, record_data)

    def endLesson(self, lesson_id):
        """ 删除课堂状态记录

        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:LESSON_ID:xxx
        key = self.__PREFIX + ':' + str(lesson_id)
        self.__conn.delete(key)


class RedisForInLesson:
    """ 封装有关用户上课情况的数据库操作

        key format: STATUS:IN_LESSON:UID:xxx
        存储的是一个map
            |- uid
            |- course_id
            |- lesson_id

        key format: STATUS:LESSON_USER:LESSON_ID:xxx
        存储的是一个set，存储用户的uid
    """
    __IN_LESSON_PRIMARY_KEY = 'UID'
    __IN_LESSON_TABLE_NAME = 'IN_LESSON'
    __IN_LESSON_PREFIX = REDIS_DB_NAME + ':' + __IN_LESSON_TABLE_NAME + ':' + __IN_LESSON_PRIMARY_KEY

    __LESSON_USER_PRIMARY_KEY = 'LESSON_ID'
    __LESSON_USER_TABLE_NAME = 'LESSON_USER'
    __LESSON_USER_PREFIX = REDIS_DB_NAME + ':' + __LESSON_USER_TABLE_NAME + ':' + __LESSON_USER_PRIMARY_KEY

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
        key = self.__IN_LESSON_PREFIX + ':' + str(uid)
        record_data = {
            'uid': uid,
            'course_id': course_id,
            'lesson_id': lesson_id
        }
        self.__conn.hmset(key, record_data)

        # format: STATUS:LESSON_USER:LESSON_ID:xxx
        key = self.__LESSON_USER_PREFIX + ':' + str(lesson_id)
        self.__conn.sadd(key, str(uid))

    def quitLesson(self, uid):
        """ 用户退出当前课堂

            把该key删除
        :param uid: 用户唯一标识
        :return:
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__IN_LESSON_PREFIX + ':' + str(uid)
        lesson_id = self.getLessonID(uid=str(uid))
        self.__conn.delete(key)

        # format: STATUS:LESSON_USER:LESSON_ID:xxx
        key = self.__LESSON_USER_PREFIX + ':' + str(lesson_id)
        self.__conn.srem(key, str(uid))

    def getLessonUsersUID(self, lesson_id):
        """ 获取参与该课的所有用户ID

        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        # format: STATUS:LESSON_USER:LESSON_ID:xxx
        key = self.__LESSON_USER_PREFIX + ':' + str(lesson_id)
        uid_arr = self.__conn.smembers(key)

        return uid_arr

    def isInLesson(self, uid):
        """ 查询用户是否在上课

        :param uid: 用户唯一标识
        :return: True - 在课室中/正在上课（即Waiting或Online状态）
                 False - 空闲状态
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__IN_LESSON_PREFIX + ':' + str(uid)

        return self.__conn.hexists(key)

    def getLessonID(self, uid):
        """ 获取该用户当前课堂的id

        :param uid: 用户唯一标识
        :return: id - 存在（在课室中/正在上课）
                 None - 不存在（空闲状态）
        """
        # format: STATUS:LESSON_STATUS:UID:xxx
        key = self.__IN_LESSON_PREFIX + ':' + str(uid)

        return self.__conn.hget(key, 'lesson_id')
