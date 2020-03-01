import time

from flask import request, Blueprint
import json
import os
import random

from src.httpServer.conf.conf import COURSE_PICTURE_PATH
from src.edu import ErrorCode
from src.httpServer.services.mysql.courseService import CourseService
from src.httpServer.services.mysql.joinCourseService import JoinCourseService

# 建立蓝图
course = Blueprint(name='course', import_name=__name__)


@course.route('/getCourseBasicInfo', methods=['POST'])
def getCourseBasicInfo():
    """
        获取课程基础信息
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}course_id
    :return:
        {string}course_id
        {int}create_timestamp
    """
    request_data = json.loads(request.form["json"])

    course_obj, err = CourseService().getCourseByCourseId(course_id=int(request_data["course_id"]))
    return_data = {
        "error_code": err,
        "course_id": None,
        "create_timestamp": None
    }

    if course_obj is not None:
        return_data["course_id"] = str(course_obj.id)
        return_data["create_timestamp"] = int(course_obj.create_timestamp)

    return return_data


@course.route('/createCourse', methods=['POST'])
def createCourse():
    """
        创建课程
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}course_name
        {string}classify
        {string}introduction
    :return:
        {int}error_code
        {string}course_id
    """
    request_data = json.loads(request.form["json"])

    course_obj, err = CourseService().insertCourse(course_name=request_data["course_name"],
                                                   classify=request_data["classify"],
                                                   creator_id=int(request_data["uid"]),
                                                   introduction=request_data["introduction"])
    if err == ErrorCode.NoError:
        join_course_service = JoinCourseService()
        join_course_obj, err = join_course_service.insertJoinCourse(course_id=int(course_obj.id),
                                                                    uid=int(request_data["uid"]))

    return_data = {
        "error_code": err,
        "course_id": str(course_obj.id)
    }

    return return_data


@course.route('/uploadCoursePicture', methods=['POST'])
def uploadCoursePicture():
    """
        上传课程图片
        Params:
        {int}account_type
        {string}uid
        {string}username
        {string}course_id
    :return:
        {int}error_code
    """
    request_data = json.loads(request.form["json"])
    request_file = request.files["file"]

    # 存储的相对路径
    relative_path = request_data["course_id"]
    absolute_path = COURSE_PICTURE_PATH + "/" + relative_path
    # 检测路径是否存在，不存在则创建
    if not os.path.exists(absolute_path):
        os.makedirs(absolute_path)

    file_relative_path = relative_path + "/" + request_data["filename"]
    file_absolute_path = COURSE_PICTURE_PATH + "/" + file_relative_path
    request_file.save(file_absolute_path)

    res, err = CourseService().updateCoursePicture(course_id=int(request_data["course_id"]),
                                                   path=file_relative_path)
    return_data = {
        "error_code": err
    }

    return return_data


@course.route('/getConcCmprChartData', methods=['POST'])
def getConcCmprChartData():
    """
       获取课程中课堂专注度对比数据（近10堂课）
       Params:
       {int}account_type
       {string}uid
       {string}username
       {string}course_id
   :return:
       {int}error_code
       {jsonArray}value
       {jsonArray}x_label
   """
    time.sleep(3)
    err = ErrorCode.NoError
    return_data = {
        "error_code": err,
        "value": [random.randint(0, 100), random.randint(0, 100),
                  random.randint(0, 100), random.randint(0, 100),
                  random.randint(0, 100), random.randint(0, 100),
                  random.randint(0, 100), random.randint(0, 100),
                  random.randint(0, 100), random.randint(0, 100)],
        "x_label": ['10-21', '10-22', '10-23', '10-24', '10-25',
                    '10-26', '10-27', '10-28', '10-29', '10-30', ]
    }

    return return_data


@course.route('/getConcRankData', methods=['POST'])
def getConcRankData():
    """
       获取课程中学生专注度排行
       Params:
       {int}account_type
       {string}uid
       {string}username
       {string}course_id
   :return:
       {int}error_code
       {jsonArray}rank_list
   """
    time.sleep(3)
    item = {"uid": 10001, "user_pic": "null_str", "username": "王小明", "times": 10, "concentration": 89, "rank": 1}
    err = ErrorCode.NoError
    return_data = {
        "error_code": err,
        "rank_list": [item, item, item, item, item, item]
    }

    return return_data

# @course.route('/getCourseIntroduction', methods=['POST'])
# def getCourseIntroduction():
#     return_data = {
#         "introduction_text": "通过本课程的学习，使学生了解软件工程的基本概念、基本原理、开发软件项目的工程化的方法和技\
#         术及在开发过程中应遵循的流程、准则、标准和规范等；熟悉软件项目开发和维护的一般过程；熟练掌握软件需求分析、设计\
#         、编码和测试等阶段的主要思想和技术方法，并且能够利用所学知识进行各种软件项目的实际开发实践。"
#     }
#
#     print(request.form["json"])
#
#     return return_data
#
#
# @course.route('/getCourseNotice', methods=['POST'])
# def getCourseNotice():
#     return_data = {
#         "notice_text": "暂无公告"
#     }
#
#     print(request.form["json"])
#
#     return return_data
