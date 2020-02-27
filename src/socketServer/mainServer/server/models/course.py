from sqlalchemy import Column, String, text
from sqlalchemy.dialects.mysql import INTEGER

from src.socketServer.utils.mysqlDb import Base


class Course(Base):
    __tablename__ = 'course'

    id = Column(INTEGER(11), primary_key=True, comment='课程唯一标识')
    name = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='课程名')
    key = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='选课码')
    classify = Column(String(255), server_default=text("'null_str'"), comment='课程分类')
    creator_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'-1'"), comment='课程创建人唯一标识')
    create_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='课程创建时间')
    status = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='课程状态（0-未开始，1-进行中，2-不可中途加入，3-等待中）')
    notice = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='课程介绍')
    introduction = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='课程公告')
    joinable = Column(INTEGER(11), server_default=text("'1'"), comment='是否可以加入（0-不可加入，1-可加入）')
    pic_path = Column(String(255), server_default=text("'null_str'"), comment='课程封面相对地址')
