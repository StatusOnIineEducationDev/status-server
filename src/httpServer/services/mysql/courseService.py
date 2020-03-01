import time

from src.httpServer.models.joinCourse import JoinCourse
from src.httpServer.utils.mysqlDb import getMySQLSession
from src.edu import ErrorCode
from src.httpServer.models.course import Course


class CourseService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

    def getCourseByCourseId(self, course_id):
        """ 获取课程模型
        :param course_id: 课程id
        :return: 存在返回course对象，否则返回None
        """
        course = self.session.query(Course).filter(Course.id == int(course_id)).one_or_none()

        err = ErrorCode.NoError
        if course is None:
            err = ErrorCode.CourseResourceNotFoundError

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
        tuple_list = self.session.query(Course.id, Course.name).\
            filter(JoinCourse.course_id == Course.id, JoinCourse.uid == int(uid)).all()
        course_list = []
        for data in tuple_list:
            course = {
                'course_id': str(data[0]),
                'course_name': data[1]
            }
            course_list.append(course)

        return course_list, ErrorCode.NoError
    
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
        course = Course(classify=classify, creator_id=int(creator_id), name=course_name,
                        introduction=introduction, create_timestamp=create_timestamp)
        self.session.add(course)
        self.session.commit()

        # 同一时间点一个用户也只能创建一个课程
        # 通过creator_id和create_timestamp可以唯一确定一个课程
        course = self.session.query(Course)\
            .filter(Course.creator_id == int(creator_id), Course.create_timestamp == create_timestamp).one_or_none()

        return course, ErrorCode.NoError

    def updateCoursePicture(self, course_id, path):
        course = self.session.query(Course).filter(Course.id == int(course_id)).one_or_none()

        if course is not None:
            course.pic_path = path
            self.session.commit()

        return course, ErrorCode.NoError



