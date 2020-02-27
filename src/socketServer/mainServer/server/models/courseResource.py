from sqlalchemy import Column, Float, ForeignKey, Index, String, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from src.socketServer.utils.mysqlDb import Base


class CourseResource(Base):
    __tablename__ = 'course_resource'
    __table_args__ = (
        Index('course_id_2', 'course_id', 'title', unique=True),
    )

    id = Column(INTEGER(11), primary_key=True, comment='课程资源的唯一标识')
    course_id = Column(ForeignKey('course.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                       server_default=text("'-1'"), comment='课程的唯一标识')
    title = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='资源标题')
    filename = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='文件名')
    type = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='文件类型')
    upload_timestamp = Column(INTEGER(11), nullable=False, server_default=text("'-1'"), comment='上传时间')
    uploader_id = Column(ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True,
                         server_default=text("'-1'"), comment='资源上传者的唯一标识')
    path = Column(String(255), nullable=False, server_default=text("'null_str'"), comment='文件存储路径')
    size = Column(Float(asdecimal=True), nullable=False, server_default=text("'-1'"), comment='文件大小')

    course = relationship('Course')
    uploader = relationship('User')
