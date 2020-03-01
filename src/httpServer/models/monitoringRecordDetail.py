from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from src.socketServer.utils.mysqlDb import Base


class MonitoringRecordDetail(Base):
    __tablename__ = 'monitoring_record_detail'

    id = Column(INTEGER(11), primary_key=True, comment='记录的唯一标识')
    record_id = Column(ForeignKey('monitoring_record.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                       index=True, server_default=text("'-1'"), comment='总记录的唯一标识')
    course_id = Column(ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程的唯一标识')
    lesson_id = Column(ForeignKey('lesson.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程下课堂的唯一标识')
    uid = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                 server_default=text("'-1'"), comment='用户的唯一标识')
    toward_score = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='朝向得分')
    emotion_score = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='表情得分')
    record_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='该条记录的时间戳')

    course = relationship('Course')
    lesson = relationship('Lesson')
    record = relationship('MonitoringRecord')
    user = relationship('User')
