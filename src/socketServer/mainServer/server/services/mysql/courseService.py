from src.socketServer.mainServer.server.models.joinCourse import JoinCourse
from src.socketServer.mainServer.server.models.user import User
from src.socketServer.utils.mysqlDb import getMySQLSession


class CourseService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

    def getAllUsername(self, course_id):
        """ 获取该课程的所有用户名

        :param course_id: 课程唯一标识
        :return: 若创建成功则返回元组列表(uid, username)
        """
        tuple_list = self.session.query(JoinCourse.uid, User.name).\
            filter(JoinCourse.course_id == course_id, JoinCourse.uid == User.id).all()

        return tuple_list
