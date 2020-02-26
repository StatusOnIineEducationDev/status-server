class JoinLesson:
    def __init__(self, id=None, lesson_id=None, uid=None, join_timestamp=None, quit_timestamp=None):
        self.id = id   # 记录唯一标识
        self.lesson_id = lesson_id   # 课程下课堂唯一标识
        self.uid = uid  # 用户唯一标识
        self.join_timestamp = join_timestamp  # 加入课堂的时间
        self.quit_timestamp = quit_timestamp  # 退出课堂的时间
