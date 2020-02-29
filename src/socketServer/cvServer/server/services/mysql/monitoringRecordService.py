import time

from src.socketServer.cvServer.server.models.monitoringRecord import MonitoringRecord
from src.socketServer.mainServer.server.models.lesson import Lesson
from src.socketServer.utils.mysqlDb import getMySQLSession


class MonitoringRecordService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

    def insertRecord(self, course_id, lesson_id, uid, concentration_value, begin_timestamp, end_timestamp):
        """ 插入一条记录

        :param course_id: 课程的唯一标识
        :param lesson_id: 课程下课堂的唯一标识
        :param uid: 用户的唯一标识
        :param concentration_value: 专注度数值
        :param begin_timestamp: 该条记录的起始时间
        :param end_timestamp: 该条记录的终止时间
        :return:
        """
        record = MonitoringRecord(course_id=course_id, lesson_id=lesson_id, uid=uid,
                                  concentration_value=concentration_value,
                                  begin_timestamp=begin_timestamp, end_timestamp=end_timestamp)
        self.session.add(record)
        self.session.commit()

    def insertManyRecords(self, records):
        """ 插入多条数据

        :param records: 多条记录
        :return:
        """
        self.session.add_all(records)
        self.session.commit()

