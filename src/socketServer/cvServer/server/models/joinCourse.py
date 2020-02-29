from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from src.socketServer.utils.mysqlDb import Base


class JoinCourse(Base):
    __tablename__ = 'join_course'

    id = Column(INTEGER(11), primary_key=True, comment='记录唯一标识')
    course_id = Column(ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程唯一标识')
    uid = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                 server_default=text("'-1'"), comment='用户唯一标识')
    join_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='加入课程的时间')

    course = relationship('Course')
    user = relationship('User')
