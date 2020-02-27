from src.edu import CourseStatus
from src.socketServer.utils.redisDb import Redis
from src.socketServer.cvServer.conf.conf import REDIS_DB_NAME


class RedisForCourseStatus:
    """ 封装有关课程的各种状态的数据库操作

        key format: STATUS:COURSE_STATUS:COURSE_ID:xxx
        存储的是一个值CourseStatus（参考edu.py）
    """
    __PRIMARY_KEY = 'COURSE_ID'
    __TABLE_NAME = 'COURSE_STATUS'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def createCourse(self, course_id):
        """ 插入一条课堂状态记录

        :param course_id: 课程唯一标识
        :return:
        """
        # format: STATUS:COURSE_STATUS:COURSE_ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        self.__conn.set(key, CourseStatus.OffLine)

    def getCourseStatus(self, course_id):
        """ 获取当前课程状态

        :param course_id: 课程唯一标识
        :return:
        """
        # format: STATUS:COURSE_STATUS:COURSE_ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        if not self.__conn.exists(key):
            self.createCourse(course_id=course_id)

        return int(self.__conn.get(key))

    def offLine(self, course_id):
        """ 课堂结束

        :return:
        """
        # format: STATUS:LESSON_STATUS:ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        self.__conn.set(key, CourseStatus.OffLine)

    def onLine(self, course_id):
        """ 正在上课

        :return:
        """
        # format: STATUS:LESSON_STATUS:ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        self.__conn.set(key, CourseStatus.OnLine)

    def cantJoinIn(self, course_id):
        """ 课堂不可中途加入

        :return:
        """
        # format: STATUS:LESSON_STATUS:ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        self.__conn.set(key, CourseStatus.CantJoinIn)

    def waiting(self, course_id):
        """ 在房间等待中，未开始上课

        :return:
        """
        # format: STATUS:LESSON_STATUS:ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        self.__conn.set(key, CourseStatus.Waiting)


class RedisForCourse:
    """ 封装有关课程的数据库操作

        key format: STATUS:COURSE:COURSE_ID:xxx
        存储的是一个lesson_id
        表示当前课程最近一堂课的lesson_id
    """
    __PRIMARY_KEY = 'COURSE_ID'
    __TABLE_NAME = 'COURSE'
    __PREFIX = REDIS_DB_NAME + ':' + __TABLE_NAME + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def updateLesson(self, course_id, lesson_id):
        """ 插入一条课程状态记录

        :param course_id: 课程唯一标识
        :param lesson_id: 课程下课堂唯一标识
        :return:
        """
        # format: STATUS:COURSE:COURSE_ID:xxx
        key = self.__PREFIX + ':' + str(course_id)
        self.__conn.set(key, lesson_id)

    def getLastlyLessonID(self, course_id):
        """ 获取课程最近一堂课的lesson_id

        :param course_id: 课程唯一标识
        :return:
        """
        # format: STATUS:COURSE:COURSE_ID:xxx
        key = self.__PREFIX + ':' + str(course_id)

        return self.__conn.get(key)
