from flask import request, Blueprint
import json

from src.httpServer.services.userService import UserService
from src.httpServer.services.courseService import CourseService

# 建立蓝图
user = Blueprint(name='user', import_name=__name__)


@user.route('/loginPC', methods=['POST'])
def loginPC():
    """
        登录请求
        Params:
        {int}account_type
        {string}account
        {string}pwd
    :return:
        {int}error_code
        {string}user_pic_url
        {string}uid
        {string}username
        {int}account_type
        {json}course_list
        {int}user_status
    """
    request_data = json.loads(request.form["json"])

    user_service = UserService()
    user_obj, err = user_service.loginPC(account=request_data["account"],
                                         pwd=request_data["pwd"],
                                         account_type=request_data["account_type"])

    return_data = {
        "error_code": err,
        "user_pic_url": None,
        "uid": None,
        "username": None,
        "account_type": None,
        "course_list": None,
        "user_status": None
    }
    if user_obj is not None:
        course_service = CourseService()
        course_list, err = course_service.getCourseBasicListByUid(uid=user_obj.id)

        return_data["user_pic"] = "NULL"
        return_data["uid"] = user_obj.id
        return_data["username"] = user_obj.name
        return_data["account_type"] = user_obj.type
        return_data["course_list"] = course_list
        return_data["user_status"] = user_obj.status

    return return_data


@user.route('/getCourseList', methods=['POST'])
def getCourseList():
    """
        获取课程列表
        Params:
        {int}account_type
        {string}uid
        {string}username
    :return:
        {int}error_code
        {json}course_list
    """
    request_data = json.loads(request.form["json"])

    course_service = CourseService()
    course_list, err = course_service.getCourseBasicListByUid(request_data["uid"])

    return_data = {
        "error_code": err,
        "course_list": course_list
    }

    return return_data
