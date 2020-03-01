from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from src.socketServer.utils.mysqlDb import Base


class JoinLesson(Base):
    __tablename__ = 'join_lesson'

    id = Column(INTEGER(11), primary_key=True, comment='记录唯一标识')
    lesson_id = Column(ForeignKey('lesson.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程下课堂唯一标识')
    uid = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                 server_default=text("'-1'"), comment='用户唯一标识')
    join_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='加入课堂的时间')
    quit_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='退出课堂的时间')

    lesson = relationship('Lesson')
    user = relationship('User')
