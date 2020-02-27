from src.httpServer.utils.mysql import *
from src.edu import *
from src.httpServer.models.user import User


class UserService:
    def __init__(self):
        # 连接数据库
        self.conn = getDatabaseConnection()
        self.cursor = self.conn.cursor()

    def loginPC(self, account, pwd, account_type):
        """
            用户登录
            除了核对账号密码外
            还需核对账号类型
        :param account: 用户输入的账号
        :param pwd: 用户输入的密码
        :param account_type: 用户输入的账号类型
        :return: 存在且所有参数核对无误则返回user对象，否则返回None
        """
        sql = "SELECT * FROM user WHERE account=%s"
        self.cursor.execute(sql, account)
        res = self.cursor.fetchall()

        user = None
        err = ErrorCode.NoError
        if len(res) == 0:
            err = ErrorCode.AccountNotFoundError
        else:
            data = res[0]  # 返回是一个列表，取第一个（也只有一个）

            if data["type"] != account_type:
                err = ErrorCode.AccountTypeError
            elif data["pwd"] != pwd:
                err = ErrorCode.PasswordError
            else:
                user = User(id=str(data["id"]), open_id=data["open_id"], account=data["account"],
                            name=data["name"], type=data["type"],  phone_num=data["phone_num"],
                            pwd=data["pwd"],  create_timestamp=data["create_timestamp"], status=data["status"])

        return user, err
