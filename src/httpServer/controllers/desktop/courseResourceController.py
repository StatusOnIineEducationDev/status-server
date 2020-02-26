from flask import request, Blueprint, send_from_directory
import json
import os

from src.httpServer.config.conf import *
from src.httpServer.services.courseResourceService import CourseResourceService

# 建立蓝图
courseResource = Blueprint(name='courseResource', import_name=__name__)


@courseResource.route('/getCourseResourceList', methods=['POST'])
def getCourseResourceList():
    """
        获取课程资源列表
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}course_id
    :return:
        {int}error_code
        {json}file_info_list
    """
    request_data = json.loads(request.form["json"])

    course_resource_service = CourseResourceService()
    res, err = course_resource_service.getCourseResourceListByCourseId(course_id=request_data["course_id"])
    return_data = {
        "error_code": err,
        "file_info_list": res
    }

    return return_data


@courseResource.route('/downloadCourseResource', methods=['POST'])
def downloadCourseResource():
    """
        下载课程资源
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}file_id
    :return:
        file
    """
    request_data = json.loads(request.form["json"])

    course_resource_service = CourseResourceService()
    course_resource, err = course_resource_service.getCourseResourceByFileId(file_id=request_data["file_id"])

    directory = COURSE_RESOURCE_PATH + "/" + course_resource.course_id + "/" + course_resource.title

    return send_from_directory(directory=directory,
                               filename=course_resource.filename,
                               as_attachment=True)


@courseResource.route('/uploadCourseResource', methods=['POST'])
def uploadCourseResource():
    """
        上传课程资源
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}course_id
        {string}resource_title
        {string}filename
        {double}file_size
    :return:
        {int}error_code
    """
    request_data = json.loads(request.form["json"])
    request_file = request.files["file"]

    # 存储的相对路径
    relative_path = request_data["course_id"] + "/" + request_data["resource_title"]
    absolute_path = COURSE_RESOURCE_PATH + "/" + relative_path
    # 检测路径是否存在，不存在则创建
    if not os.path.exists(absolute_path):
        os.makedirs(absolute_path)

    file_relative_path = relative_path + "/" + request_data["filename"]
    file_absolute_path = COURSE_RESOURCE_PATH + "/" + file_relative_path
    request_file.save(file_absolute_path)

    course_resource_service = CourseResourceService()
    res, err = course_resource_service.insertCourseResource(course_id=request_data["course_id"],
                                                            title=request_data["resource_title"],
                                                            filename=request_data["filename"],
                                                            uploader_id=request_data["uid"],
                                                            path=file_relative_path,
                                                            size=request_data["file_size"])

    return_data = {
        "error_code": err
    }

    return return_data


@courseResource.route('/deleteCourseResource', methods=['POST'])
def deleteCourseResource():
    """
        删除课程资源
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}file_id
    :return:
        {int}error_code
    """
    request_data = json.loads(request.form["json"])

    course_resource_service = CourseResourceService()
    res, err = course_resource_service.deleteCourseResourceByFileId(file_id=request_data["file_id"])

    return_data = {
        "error_code": err
    }

    return return_data
