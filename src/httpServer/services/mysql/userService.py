from src.httpServer.utils.mysqlDb import getMySQLSession
from src.edu import ErrorCode
from src.httpServer.models.user import User


class UserService:
    def __init__(self):
        # 连接数据库
        self.session = getMySQLSession()

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
        user = self.session.query(User).filter(User.account == account).one_or_none()

        err = ErrorCode.NoError
        if user is None:
            err = ErrorCode.AccountNotFoundError
        else:
            if user.type != account_type:
                err = ErrorCode.AccountTypeError
            elif user.pwd != pwd:
                err = ErrorCode.PasswordError

        return user, err
