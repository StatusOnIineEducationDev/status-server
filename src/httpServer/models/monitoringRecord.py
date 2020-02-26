class MonitoringRecord:
    def __init__(self, id=None, course_id=None, lesson_id=None, uid=None, concentration_value=None, fatigue_value=None,
                 begin_timestamp=None, end_timestamp=None):
        self.id = id  # 记录的唯一标识
        self.course_id = course_id  # 课程唯一标识
        self.lesson_id = lesson_id  # 课程下课堂的唯一标识
        self.uid = uid  # 用户的唯一标识
        self.concentration_value = concentration_value  # 专注度数值
        self.fatigue_value = fatigue_value  # 疲劳度数值
        self.begin_timestamp = begin_timestamp  # 该条记录的起始时间
        self.end_timestamp = end_timestamp  # 该条记录的终止时间
