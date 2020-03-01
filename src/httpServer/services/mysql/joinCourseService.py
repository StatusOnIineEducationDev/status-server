import time

from src.edu import ErrorCode
from src.httpServer.models.joinCourse import JoinCourse
from src.httpServer.utils.mysqlDb import getMySQLSession


class JoinCourseService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

    def insertJoinCourse(self, course_id, uid):
        join_timestamp = int(time.time())

        join_course = JoinCourse(course_id=int(course_id), uid=int(uid), join_timestamp=join_timestamp)
        self.session.add(join_course)
        self.session.commit()

        join_course = self.session.query(JoinCourse) \
            .filter(JoinCourse.course_id == int(course_id), JoinCourse.uid == int(uid)).one_or_none()

        return join_course, ErrorCode.NoError
