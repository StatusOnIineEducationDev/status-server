class Lesson:
    def __init__(self, id=None, course_id=None, teacher_id=None, create_timestamp=None, begin_timestamp=None,
                 end_timestamp=None):
        self.id = id  # 课程下课堂的唯一标识
        self.course_id = course_id  # 课程唯一标识
        self.teacher_id = teacher_id  # 教师唯一标识
        self.create_timestamp = create_timestamp  # 课堂创建时间
        self.begin_timestamp = begin_timestamp  # 课堂开始时间
        self.end_timestamp = end_timestamp  # 课堂开始时间
