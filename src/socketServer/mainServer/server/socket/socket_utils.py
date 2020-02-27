import json
import struct

from src.edu import *


def send(connection, data):
        if isinstance(connection, list):
            for connection_temp in connection:
                try:
                    connection_temp["socket"].send(struct.pack("!i", len(json.dumps(data))))
                    connection_temp["socket"].send(json.dumps(data).encode())
                except Exception:
                    pass
        else:
            try:
                connection["socket"].send(struct.pack("!i", len(json.dumps(data))))
                connection["socket"].send(json.dumps(data).encode())
            except Exception:
                pass


def reply(request, data):
    try:
        request.send(struct.pack("!i", len(json.dumps(data))))
        request.send(json.dumps(data).encode())
    except Exception:
        pass


def findLessonByLessonId(lessons, lesson_id):
    lesson = None

    for lesson_temp in lessons:
        if lesson_temp["lesson_id"] == lesson_id:
            lesson = lesson_temp

    return lesson


def findConnectionByUid(connection_pool, uid):
    connection = None
    for connection_temp in connection_pool:
        if connection_temp["uid"] == uid:
            connection = connection_temp
            break

    return connection


def removeConnectionByUid(connection_pool, uid):
    for connection_temp in connection_pool:
        if connection_temp["uid"] == uid:
            connection_pool.remove(connection_temp)
            break


def findConnectionByCourseId(connection_pool, course_id):
    connection_list = []
    for connection_temp in connection_pool:
        if connection_temp["course_id"] == course_id:
            connection_list.append(connection_temp)

    return connection_list


def findConnectionByLessonId(connection_pool, lesson_id):
    connection_list = []
    for connection_temp in connection_pool:
        if connection_temp["lesson_id"] == lesson_id:
            connection_list.append(connection_temp)

    return connection_list


def findConnectionByAccountType(connection_pool, account_type):
    connection_list = []
    for connection_temp in connection_pool:
        if connection_temp["account_type"] == account_type:
            connection_list.append(connection_temp)

    return connection_list


def findTeacherConnectionInLesson(connection_pool, lesson_id):
    connection = None
    for connection_temp in connection_pool:
        if connection_temp["lesson_id"] == lesson_id and connection_temp["account_type"] == AccountType.Teacher:
            connection = connection_temp

    return connection


def findOtherConnectionInLesson(connection_pool, lesson_id, my_uid):
    connection_list = []
    for connection_temp in connection_pool:
        print(connection_temp)
        if connection_temp["lesson_id"] == lesson_id and connection_temp["uid"] != my_uid:
            connection_list.append(connection_temp)

    return connection_list


def getSpeechStatus(connection_pool, uid):
    connection = findConnectionByUid(connection_pool=connection_pool, uid=uid)
    status = connection["status"]

    return status["speech_status"]


def setSpeechStatus(connection_pool, uid, speech_status):
    connection = findConnectionByUid(connection_pool=connection_pool, uid=uid)
    status = connection["status"]
    status["speech_status"] = speech_status

