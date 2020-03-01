import time

from src.edu import ErrorCode
from src.httpServer.models.courseResource import CourseResource
from src.httpServer.utils.mysqlDb import getMySQLSession


class CourseResourceService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

    def getCourseResourceByFileId(self, file_id):
        """
            下载课程资源
        :param file_id: 文件（或资源）id
        :return: 返回真实文件，反映为下载
        """
        course_resource = self.session.query(CourseResource).\
            filter(CourseResource.id == int(file_id)).one_or_none()

        err = ErrorCode.NoError
        if course_resource is None:
            err = ErrorCode.CourseResourceNotFoundError

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
        file_type = filename[filename.rfind(".") + 1:]
        upload_timestamp = int(time.time())

        err = ErrorCode.NoError

        course_resource = CourseResource(course_id=int(course_id), title=title,
                                         filename=filename, type=file_type,
                                         upload_timestamp=upload_timestamp,
                                         uploader_id=uploader_id, path=path,
                                         size=size)
        self.session.add(course_resource)
        self.session.commit()

        course_resource = self.session.query(CourseResource) \
            .filter(CourseResource.course_id == course_id, CourseResource.title == title).one_or_none()

        # err = ErrorCode.CourseResourceTitleDuplicateError

        return course_resource, err

    def deleteCourseResourceByFileId(self, file_id):
        """
            移除某一课程资源
            仅移除数据库中的记录
        :param file_id: 需要删除的文件（或资源）id
        :return:
        """
        course_resource = self.session.query(CourseResource).\
            filter(CourseResource.id == int(file_id)).one_or_none()

        err = ErrorCode.NoError
        if course_resource is None:
            err = ErrorCode.CourseResourceNotFoundError
        else:
            self.session.delete(course_resource)
            self.session.commit()

        return course_resource, err

    def getCourseResourceListByCourseId(self, course_id):
        """
            获取课程资源列表（course_id、 course_name）
            通过course_idd获取获取课程资源列表
        :param course_id: 课程id
        :return: 返回列表res，若无资源则为空列表
                 其中元素为字典，keys如下
                 |-data
                    |-file_id
                    |-resource_title
                    |-filename
                    |-upload_timestamp
                    |-uploader
                    |-file_size
        """
        result = self.session.query(CourseResource).\
            filter(CourseResource.course_id == int(course_id)).all()
        resource_list = []
        for data in result:
            obj = {
                'file_id': str(data.id),
                'resource_title': str(data.title),
                'filename': str(data.filename),
                'upload_timestamp': int(data.upload_timestamp),
                'uploader': str(data.uploader.name),
                'file_size': int(data.size)
            }
            resource_list.append(obj)

        return resource_list, ErrorCode.NoError
