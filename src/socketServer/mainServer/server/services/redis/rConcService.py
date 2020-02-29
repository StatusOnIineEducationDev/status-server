import json

from src.socketServer.utils.redisDb import Redis
from src.socketServer.cvServer.conf.conf import REDIS_DB_NAME


class RedisForDetails:
    """ 封装有关每帧检测数据记录的数据库操作

        每位用户的记录在redis中以list形式存储
        一堂课的所有详细记录都将会存储在这个list中
        仅通过一个key（format: STATUS:CONC_DETAILS:UID:xxx）即可以访问到该课的所有记录

        由于此格式的key是以uid作为主键的，同时也没有对其他键进行维护
        因此在redis中存储的仅是一堂课中的专注度信息，课堂结束后将转储到mysql中
    """
    __PRIMARY_KEY = 'UID'

    __DETAILS = 'CONC_DETAILS'
    __USEFUL_DETAILS = 'CONC_USEFUL_DETAILS'

    __DETAILS_PREFIX = REDIS_DB_NAME + ':' + __DETAILS + ':' + __PRIMARY_KEY
    __USEFUL_DETAILS_PREFIX = REDIS_DB_NAME + ':' + __USEFUL_DETAILS + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def addDetail(self, is_succeed, uid, course_id, lesson_id, timestamp, emotion,
                  is_blinked, is_yawned, h_angle, v_angle):
        """ 插入一条详细记录

            详细记录是生成最终专注度记录的依据
            每10条详细记录可用于生成1条最终记录
        :param is_succeed: 是否成功识别到图像中的人脸（该条记录是否有用）
        :param uid: 用户唯一标识
        :param course_id: 课程唯一标识
        :param lesson_id: 课程下课堂唯一标识
        :param timestamp: 该条记录的时间戳（指的是图像截取的时间，而非记录生成的时间）
        :param emotion: 表情
        :param is_blinked: 是否有眨眼
        :param is_yawned: 是否有打哈欠
        :param h_angle: 头部的水平转动角度
        :param v_angle: 头部的垂直转动角度
        :return:
        """
        # format: STATUS:DETAILS:UID:xxx
        key = self.__DETAILS_PREFIX + ':' + uid
        record_data = {
            'is_succeed': is_succeed,
            'uid': uid,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'timestamp': timestamp,
            'emotion': emotion,
            'is_blinked': is_blinked,
            'is_yawned': is_yawned,
            'h_angle': h_angle,
            'v_angle': v_angle
        }
        # redis的list中不能直接存储data类型
        # 需先data转换为str
        self.__conn.lpush(key, json.dumps(record_data))

    def addUsefulDetail(self, is_succeed, uid, course_id, lesson_id, timestamp, emotion,
                        is_blinked, is_yawned, h_angle, v_angle):
        """ 插入一条能用于生成最终记录的详细记录

        :param is_succeed: 是否成功识别到图像中的人脸（该条记录是否有用）
        :param uid: 用户唯一标识
        :param course_id: 课程唯一标识
        :param lesson_id: 课程下课堂唯一标识
        :param timestamp: 该条记录的时间戳（指的是图像截取的时间，而非记录生成的时间）
        :param emotion: 表情
        :param is_blinked: 是否有眨眼
        :param is_yawned: 是否有打哈欠
        :param h_angle: 头部的水平转动角度
        :param v_angle: 头部的垂直转动角度
        :return:
            满10条记录后会返回True，以及10条json格式数据列表
            否则返回False，以及返回[]
        """
        # format: STATUS:USEFUL_DETAILS:UID:xxx
        key = self.__USEFUL_DETAILS_PREFIX + ':' + uid
        record_data = {
            'is_succeed': is_succeed,
            'uid': uid,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'timestamp': timestamp,
            'emotion': emotion,
            'is_blinked': is_blinked,
            'is_yawned': is_yawned,
            'h_angle': h_angle,
            'v_angle': v_angle
        }
        # redis的list中不能直接存储data类型
        # 需先data转换为str
        #
        # 满10条记录后会返回True
        if self.__conn.lpush(key, json.dumps(record_data)) >= 10:
            return True
        else:
            return False

    def getUsefulDetails(self, uid):
        """ 获取并清空可用的十条详细记录

        :param uid: 用户唯一标识
        :return:
            json格式数据
        """
        # format: STATUS:USEFUL_DETAILS:UID:xxx
        key = self.__USEFUL_DETAILS_PREFIX + ':' + uid
        data_list = []
        str_list = self.__conn.lrange(key, 0, 9)
        for data_str in str_list:
            data_list.append(json.loads(data_str))
        self.__conn.delete(key)

        return data_list

    def refresh(self, uid):
        """ 为避免上次课堂的残留记录影响，重新加入需要清除一下

        :param uid: 用户唯一标识
        :return:
        """
        key = self.__USEFUL_DETAILS_PREFIX + ':' + str(uid)
        self.__conn.delete(key)


class RedisForConc:
    """ 封装有关专注度记录的数据库操作

        每位用户的记录在redis中以list形式存储
        一堂课的所有详细记录都将会存储在这个list中
        仅通过一个key（format: STATUS:CONCDETAILS:UID:xxx）即可以访问到该课的所有记录

        由于此格式的key是以uid作为主键的，同时也没有对其他键进行维护
        因此在redis中存储的仅是一堂课中的专注度信息，课堂结束后将转储到mysql中
    """
    __PRIMARY_KEY = 'LESSON_ID'

    __CONC = 'CONC'

    __PREFIX = REDIS_DB_NAME + ':' + __CONC + ':' + __PRIMARY_KEY

    def __init__(self):
        self.__conn = Redis().conn

    def addConcRecord(self, uid, course_id, lesson_id, begin_timestamp,
                      end_timestamp, conc_score):
        """ 插入一条最终记录

        :param uid: 用户唯一标识
        :param course_id: 课程唯一标识
        :param lesson_id: 课程下课堂唯一标识
        :param begin_timestamp: 该条记录生成依据的起始时间
        :param end_timestamp: 该条记录生成依据的结束时间
        :param conc_score: 专注度评分
        :return:
        """
        # format: STATUS:CONC:LESSON_ID:xxx
        key = self.__PREFIX + ':' + lesson_id
        record_data = {
            'uid': uid,
            'course_id': course_id,
            'lesson_id': lesson_id,
            'begin_timestamp': begin_timestamp,
            'end_timestamp': end_timestamp,
            'conc_score': conc_score
        }
        # redis的list中不能直接存储data类型
        # 需先data转换为str
        self.__conn.lpush(key, json.dumps(record_data))

    def getConcRecords(self, lesson_id):
        """ 获取该课程下课堂（lesson）的专注度信息

        :param lesson_id: 课程下课堂唯一标识
        :return:
            json格式数据
        """
        # format: STATUS:CONC:LESSON_ID:xxx
        key = self.__PREFIX + ':' + lesson_id
        data_list = []
        str_list = self.__conn.lrange(key, 0, -1)
        for data_str in str_list:
            data_list.append(json.loads(data_str))

        return data_list