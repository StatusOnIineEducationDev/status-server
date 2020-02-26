import time

from src.httpServer.utils.mysql import *
from src.edu import *
from src.httpServer.models.courseResource import CourseResource


class CourseResourceService:
    def __init__(self):
        # 连接数据库
        self.conn = getDatabaseConnection()
        self.cursor = self.conn.cursor()

    def getCourseResourceByFileId(self, file_id):
        """
            下载课程资源
        :param file_id: 文件（或资源）id
        :return: 返回真实文件，反映为下载
        """
        sql = "SELECT * FROM course_resource WHERE id=%s"
        self.cursor.execute(sql, file_id)
        res = self.cursor.fetchall()

        course_resource = None
        err = ErrorCode.NoError
        if len(res) == 0:
            err = ErrorCode.CourseResourceNotFoundError
        else:
            dict = res[0]  # 返回是一个列表，取第一个（也只有一个）
            course_resource = CourseResource(id=str(dict["id"]), course_id=str(dict["course_id"]), title=dict["title"],
                                             filename=dict["filename"], type=dict["type"],
                                             upload_timestamp=dict["upload_timestamp"],
                                             uploader_id=str(dict["uploader_id"]),
                                             path=dict["path"])

        return course_resource, err

    def insertCourseResource(self, course_id, title, filename, uploader_id, path, size):
        """
            插入一条课程资源记录
            注意course_resource表有course_id与tile的唯一性约束
        :param course_id: 课程id
        :param title: 资源标题
        :param filename: 文件名
        :param uploader_id: 上传者id
        :param path: 相对存储路径
        :param size: 文件大小
        :return: 插入成功返回course_resource对象，否则返回None
        """
        type = filename[filename.rfind(".") + 1:]
        upload_timestamp = int(time.time())

        course_resource = None
        err = ErrorCode.NoError
        try:
            sql = "INSERT INTO " \
                  "course_resource (course_id, title, filename, type, upload_timestamp, uploader_id, path, size) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(sql, (course_id, title, filename, type, upload_timestamp, uploader_id, path, size))

            sql = "SELECT * FROM course_resource WHERE course_id=%s AND title=%s"
            self.cursor.execute(sql, (course_id, title))
            res = self.cursor.fetchall()
            dict = res[0]
            course_resource = CourseResource(id=str(dict["id"]), course_id=str(dict["course_id"]), title=dict["title"],
                                             filename=dict["filename"], type=dict["type"],
                                             upload_timestamp=dict["upload_timestamp"],
                                             uploader_id=str(dict["uploader_id"]),
                                             path=dict["path"])
        except pymysql.err.IntegrityError:  # 完整性约束，course_id与tile的唯一性约束
            err = ErrorCode.CourseResourceTitleDuplicateError

        return course_resource, err

    def deleteCourseResourceByFileId(self, file_id):
        """
            移除某一课程资源
            仅移除数据库中的记录
        :param file_id: 需要删除的文件（或资源）id
        :return:
        """
        sql = "SELECT * FROM course_resource WHERE id=%s"
        self.cursor.execute(sql, file_id)
        res = self.cursor.fetchall()

        course_resource = None
        err = ErrorCode.NoError
        if len(res) == 0:
            err = ErrorCode.CourseResourceNotFoundError
        else:
            dict = res[0]
            course_resource = CourseResource(id=str(dict["id"]), course_id=dict["course_id"], title=dict["title"],
                                             filename=dict["filename"], type=dict["type"],
                                             upload_timestamp=dict["upload_timestamp"], uploader_id=dict["uploader_id"],
                                             path=dict["path"])

            sql = "DELETE FROM course_resource WHERE id=%s"
            self.cursor.execute(sql, file_id)

        return course_resource, err

    def getCourseResourceListByCourseId(self, course_id):
        """
            获取课程资源列表（course_id、 course_name）
            通过course_idd获取获取课程资源列表
        :param course_id: 课程id
        :return: 返回列表res，若无资源则为空列表
                 其中元素为字典，keys如下
                 |-dict
                    |-file_id
                    |-resource_title
                    |-filename
                    |-upload_timestamp
                    |-uploader
                    |-file_size
        """
        err = ErrorCode.NoError
        sql = "SELECT " \
              "CAST(course_resource.id AS CHAR) AS file_id, " \
              "title AS resource_title, filename, upload_timestamp, " \
              "name AS uploader, size AS file_size " \
              "FROM course_resource " \
              "LEFT JOIN user ON uploader_id=user.id " \
              "WHERE course_id=%s " \
              "ORDER BY upload_timestamp DESC"
        self.cursor.execute(sql, course_id)
        res = self.cursor.fetchall()

        return res, err
