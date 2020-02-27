import time

from src.socketServer.mainServer.server.models.lesson import Lesson
from src.socketServer.utils.mysqlDb import getMySQLSession


class LessonService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

    def createLesson(self, course_id, teacher_id):
        """
            创建一个课堂
        :param course_id: 课程唯一标识
        :param teacher_id: 教师唯一标识
        :return: 若创建成功则返回Lesson对象，否则返回None
        """
        # 插入一条课堂信息
        create_timestamp = int(time.time())
        lesson = Lesson(course_id=course_id, teacher_id=teacher_id, create_timestamp=create_timestamp)
        self.session.add(lesson)
        self.session.commit()

        # 通过course_id和create_timestamp就可以唯一确定一个课堂
        # 因为一个课程在同一时间点只能有一个在线的课堂
        lesson = self.session.query(Lesson).filter_by(course_id=course_id, create_timestamp=create_timestamp).one()

        return lesson
