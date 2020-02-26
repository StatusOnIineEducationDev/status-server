import time

from src.httpServer.utils.mysql import *
from src.edu import *
from src.httpServer.models.joinCourse import JoinCourse


class JoinCourseService:
    def __init__(self):
        # 连接数据库
        self.conn = getDatabaseConnection()
        self.cursor = self.conn.cursor()

    def insertJoinCourse(self, course_id, uid):
        join_timestamp = int(time.time())
        sql = "INSERT INTO " \
              "join_course (course_id, uid, join_timestamp) " \
              "VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (course_id, uid, join_timestamp))

        sql = "SELECT * FROM join_course WHERE course_id=%s AND uid=%s"
        self.cursor.execute(sql, (course_id, uid))
        res = self.cursor.fetchall()
        dict = res[0]
        join_course = JoinCourse(id=str(dict["id"]), course_id=str(dict["course_id"]),
                                 uid=str(dict["uid"]), join_timestamp=dict["join_timestamp"])
        err = ErrorCode.NoError

        return join_course, err
