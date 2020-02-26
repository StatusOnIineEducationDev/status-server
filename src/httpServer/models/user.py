class User:
    def __init__(self, id=None, open_id=None, account=None, name=None, type=None, phone_num=None, pwd=None,
                 create_timestamp=None, status=None):
        self.id = id  # 用户唯一标识
        self.open_id = open_id  # 用户唯一标识（微信小程序）
        self.account = account  # 账号
        self.name = name  # 用户名
        self.type = type  # 用户类型
        self.phone_num = phone_num  # 手机号码
        self.pwd = pwd  # 密码
        self.create_timestamp = create_timestamp  # 账号创建时间
        self.status = status  # 用户当前状态
