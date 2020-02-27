import time

from src.httpServer.utils.mysql import *
from src.edu import *
from src.httpServer.models.course import Course


class CourseService:
    def __init__(self):
        # 连接数据库
        self.conn = getDatabaseConnection()
        self.cursor = self.conn.cursor()

    def getCourseByCourseId(self, course_id):
        """
            获取课程模型
        :param course_id: 课程id
        :return: 存在返回course对象，否则返回None
        """
        sql = "SELECT * FROM course WHERE id=%s"
        self.cursor.execute(sql, course_id)
        res = self.cursor.fetchall()

        course = None
        err = ErrorCode.NoError
        if len(res) == 0:
            err = ErrorCode.CourseResourceNotFoundError
        else:
            data = res[0]  # 返回是一个列表，取第一个（也只有一个）
            course = Course(id=str(data["id"]), name=data["name"], key=data["key"], classify=data["classify"],
                            creator_id=str(data["creator_id"]), create_timestamp=data["create_timestamp"],
                            status=data["status"], notice=data["notice"], introduction=data["introduction"],
                            joinable=data["joinable"], pic_path=data["pic_path"])
        return course, err

    def getCourseBasicListByUid(self, uid):
        """
            获取课程的基本信息（course_id、 course_name）
            通过用户uid获取用户加入（或创建）的课程的基本信息
        :param uid: 用户id
        :return: 返回列表res，若无课程则为空列表
                 其中元素为字典，keys如下
                 |-data
                    |-course_id
                    |-course_name
        """
        err = ErrorCode.NoError
        sql = "SELECT CAST(id AS CHAR) AS course_id, name AS course_name " \
              "FROM course " \
              "WHERE id IN (SELECT course_id FROM join_course WHERE uid=%s)"
        self.cursor.execute(sql, uid)
        res = self.cursor.fetchall()

        return res, err
    
    def insertCourse(self, course_name, classify, creator_id, introduction):
        """
            创建一个课程
            :param course_name: 课程名
            :param classify: 课程分类
            :param creator_id: 创建人id
            :param introduction: 课程介绍
            :return: 插入成功返回course对象，否则返回None
        """
        if introduction == "":
            introduction = "null_str"

        create_timestamp = int(time.time())
        sql = "INSERT INTO " \
              "course (name, classify, creator_id, introduction, create_timestamp) " \
              "VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, (course_name, classify, creator_id, introduction, create_timestamp))

        sql = "SELECT * FROM course WHERE creator_id=%s AND create_timestamp=%s"
        self.cursor.execute(sql, (creator_id, create_timestamp))
        res = self.cursor.fetchall()
        data = res[0]
        course = Course(id=str(data["id"]), name=data["name"], key=data["key"],
                        classify=data["classify"], creator_id=str(data["creator_id"]),
                        create_timestamp=data["create_timestamp"], status=data["status"],
                        notice=data["notice"], introduction=data["introduction"],
                        joinable=data["joinable"], pic_path=data["pic_path"])
        err = ErrorCode.NoError

        return course, err

    def updateCoursePicture(self, course_id, path):
        sql = "UPDATE course SET pic_path=%s WHERE id=%s"
        self.cursor.execute(sql, (path, course_id))

        sql = "SELECT * FROM course WHERE id=%s"
        self.cursor.execute(sql, course_id)
        res = self.cursor.fetchall()
        data = res[0]
        course = Course(id=str(data["id"]), name=data["name"], key=data["key"],
                        classify=data["classify"], creator_id=str(data["creator_id"]),
                        create_timestamp=data["create_timestamp"], status=data["status"],
                        notice=data["notice"], introduction=data["introduction"],
                        joinable=data["joinable"], pic_path=data["pic_path"])
        err = ErrorCode.NoError

        return course, err



