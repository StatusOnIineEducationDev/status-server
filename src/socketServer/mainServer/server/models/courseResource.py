class CourseResource:
    def __init__(self, id=None, course_id=None, title=None, filename=None, type=None, upload_timestamp=None,
                 uploader_id=None, path=None, size=None):
        self.id = id   # 课程资源的唯一标识
        self.course_id = course_id   # 课程的唯一标识
        self.title = title  # 资源标题
        self.filename = filename  # 文件名
        self.type = type  # 文件类型
        self.upload_timestamp = upload_timestamp  # 上传时间
        self.uploader_id = uploader_id  # 资源上传者的唯一标识
        self.path = path  # 文件存储路径
        self.size = size  # 文件大小
