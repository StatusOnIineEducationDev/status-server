from sqlalchemy import Column, text, String
from sqlalchemy.dialects.mysql import INTEGER

from src.socketServer.utils.mysqlDb import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(11), primary_key=True, comment='用户唯一标识')
    open_id = Column(String(28), nullable=False, server_default=text("'null_str'"), comment='用户唯一标识（微信小程序）')
    account = Column(String(255), nullable=False, unique=True, server_default=text("'null_str'"), comment='账号')
    name = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='用户名')
    type = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='账号类型（0-教师，1-学生）')
    phone_num = Column(String(11), nullable=False, server_default=text("'null_str'"), comment='手机号码')
    pwd = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='密码')
    create_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='账号创建时间')
    status = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='用户当前状态（0-空闲，1-在房间中但未开始上课，2-正在上课）')
