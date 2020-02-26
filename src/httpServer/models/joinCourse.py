class JoinCourse:
    def __init__(self, id=None, course_id=None, uid=None, join_timestamp=None):
        self.id = id   # 记录唯一标识
        self.course_id = course_id   # 课程唯一标识
        self.uid = uid  # 用户唯一标识
        self.join_timestamp = join_timestamp  # 加入课程的时间
