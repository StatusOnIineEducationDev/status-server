class MonitoringRecordDetail:
    def __init__(self, id=None, record_id=None, course_id=None, lesson_id=None, uid=None, toward_score=None,
                 emotion_score=None, record_timestamp=None):
        self.id = id  # 记录的唯一标识
        self.record_id = record_id  # 总记录的唯一标识
        self.course_id = course_id  # 课程唯一标识
        self.lesson_id = lesson_id  # 课程下课堂的唯一标识
        self.uid = uid  # 用户的唯一标识
        self.toward_score = toward_score  # 朝向得分
        self.emotion_score = emotion_score  # 表情得分
        self.record_timestamp = record_timestamp  # 该条记录的时间戳
