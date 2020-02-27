from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from src.socketServer.utils.mysqlDb import Base


class MonitoringRecord(Base):
    __tablename__ = 'monitoring_record'

    id = Column(INTEGER(11), primary_key=True, comment='记录的唯一标识')
    course_id = Column(ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程的唯一标识')
    lesson_id = Column(ForeignKey('lesson.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程下课堂的唯一标识')
    uid = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True, server_default=text("'-1'"),
                 comment='用户的唯一标识')
    concentration_value = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='专注度数值')
    begin_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='该条记录的起始时间')
    end_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='该条记录的终止时间')

    course = relationship('Course')
    lesson = relationship('Lesson')
    user = relationship('User')
