from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from src.socketServer.mainServer.server.models.course import Course
from src.socketServer.mainServer.server.models.user import User
from src.socketServer.utils.mysqlDb import Base


class Lesson(Base):
    __tablename__ = 'lesson'

    id = Column(INTEGER(11), primary_key=True, comment='课程下的课堂的唯一标识')
    course_id = Column(ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程唯一标识')
    teacher_id = Column(ForeignKey('user.id'), nullable=False, index=True, server_default=text("'-1'"),
                        comment='该课堂的教师唯一标识')
    create_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='课堂创建时间')
    begin_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='课堂开始时间')
    end_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='课堂结束时间')

    course = relationship(Course)
    teacher = relationship(User)
