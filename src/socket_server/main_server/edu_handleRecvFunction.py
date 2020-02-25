import time

from src.edu import *
from src.socket_server.main_server.edu_handleConnection import *


def createLesson(server, json_obj):
    course_id = json_obj["course_id"]
    course_name = json_obj["course_name"]
    uid = json_obj["uid"]
    account_type = json_obj["account_type"]
    username = json_obj["username"]
    create_timestamp = time.time()
    lesson_id = None
    lesson_info = None
    in_speech_now = []
    paint_command_pool = []

    if course_id in server.course_id_arr:
        pass
    else:
        lesson_id = "1001"
        # 创建的课堂（房间）信息
        lesson_info = {
            "course_id": course_id,
            "course_name": course_name,
            "lesson_id": lesson_id,
            "create_timestamp": create_timestamp,
            "begin_timestamp": create_timestamp,
            "teacher_id": uid,
            "teacher_name": username,
            "course_status": CourseStatus.Waiting,
            "chat_status": ChatStatus.Free,
            "in_speech_now": in_speech_now,
            "paint_command_pool": paint_command_pool
        }

    # 长连接信息
    connection = {
        "uid": uid,
        "account_type": account_type,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "status": {
            "speech_status": SpeechStatus.InSpeech
        },
        "socket": server.request
    }

    # 信息保存到内存
    server.lesson_connection_pool.append(connection)
    server.lessons.append(lesson_info)
    server.course_id_arr.append(course_id)

    # 创建结果返回
    return_info = {
        "command": TransportCmd.CreateLesson,
        "lesson_id": lesson_id,
        "course_id": course_id,
        "course_name": course_name,
        "teacher_id": uid,
        "teacher_name": username,
        "create_timestamp": create_timestamp,
    }
    server.request.send(struct.pack("!i", len(json.dumps(return_info))))
    server.request.send(json.dumps(return_info).encode())


def joinInLesson(server, json_obj):
    course_id = json_obj["course_id"]
    uid = json_obj["uid"]
    account_type = json_obj["account_type"]
    lesson_id = None
    teacher_id = None
    teacher_name = None
    course_name = None
    create_timestamp = None
    begin_timestamp = None
    course_status = CourseStatus.OffLine

    if course_id in server.course_id_arr:
        for lesson in server.lessons:
            if lesson["course_id"] == course_id:
                lesson_id = lesson["lesson_id"]
                course_status = lesson["course_status"]
                teacher_id = lesson["teacher_id"]
                teacher_name = lesson["teacher_name"]
                course_name = lesson["course_name"]
                create_timestamp = lesson["create_timestamp"]
                begin_timestamp = lesson["begin_timestamp"]

                # 长连接信息
                connection = {
                    "uid": uid,
                    "account_type": account_type,
                    "course_id": course_id,
                    "lesson_id": lesson_id,
                    "status": {
                        "speech_status": SpeechStatus.SpeechFree
                    },
                    "socket": server.request
                }
                # 信息保存到内存
                server.lesson_connection_pool.append(connection)

    # 结果返回
    return_info = {
        "command": TransportCmd.JoinInLesson,
        "course_status": course_status,
        "course_id": course_id,
        "course_name": course_name,
        "lesson_id": lesson_id,
        "teacher_id": teacher_id,
        "teacher_name": teacher_name,
        "create_timestamp": create_timestamp,
        "begin_timestamp": begin_timestamp
    }
    server.request.send(struct.pack("!i", len(json.dumps(return_info))))
    server.request.send(json.dumps(return_info).encode())


def beginLesson(server, json_obj):
    course_id = json_obj["course_id"]
    lesson_id = json_obj["lesson_id"]
    begin_timestamp = time.time()

    # 更改课堂状态
    lesson = findLessonByLessonId(lessons=server.lessons, lesson_id=lesson_id)
    lesson["course_status"] = CourseStatus.OnLine
    lesson["begin_timestamp"] = begin_timestamp

    # 给所有课堂中的人发送信息
    send_info = {
        "command": TransportCmd.BeginLesson,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "begin_timestamp": begin_timestamp
    }
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    send(connection_pool=server.lesson_connection_pool, connection=connection_list, data=send_info)


def endLesson(server, json_obj):
    course_id = json_obj["course_id"]
    lesson_id = json_obj["lesson_id"]
    end_timestamp = time.time()

    # 给所有课堂中的人发送信息
    send_info = {
        "command": TransportCmd.EndLesson,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "end_timestamp": end_timestamp
    }
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    send(connection_pool=server.lesson_connection_pool, connection=connection_list, data=send_info)

    # 清除connection
    for connection in server.lesson_connection_pool:
        if connection["lesson_id"] == lesson_id:
            server.lesson_connection_pool.remove(connection)
    for connection in server.paint_connection_pool:
        if connection["lesson_id"] == lesson_id:
            server.paint_connection_pool.remove(connection)
    for lesson in server.lessons:
        if lesson["lesson_id"] == lesson_id:
            server.lessons.remove(lesson)
    if course_id in server.course_id_arr:
        server.course_id_arr.remove(course_id)


def paintCommand(server, json_obj):
    course_id = json_obj["course_id"]
    lesson_id = json_obj["lesson_id"]
    uid = json_obj["uid"]
    lesson = findLessonByLessonId(server.lessons, lesson_id)

    speech_status = getSpeechStatus(connection_pool=server.lesson_connection_pool, uid=uid)
    if speech_status == SpeechStatus.InSpeech:
        # 保存
        lesson["paint_command_pool"].append(json_obj)
        # 转发给相关的用户（除自己外）
        connection_list = findOtherConnectionInLesson(connection_pool=server.paint_connection_pool,
                                                      lesson_id=lesson_id,
                                                      my_uid=uid)
        send(connection_pool=server.paint_connection_pool, connection=connection_list, data=json_obj)
        print(connection_list)


def createPaintConnection(server, json_obj):
    course_id = json_obj["course_id"]
    lesson_id = json_obj["lesson_id"]
    uid = json_obj["uid"]
    account_type = json_obj["account_type"]

    # 长连接信息
    connection = {
        "uid": uid,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "socket": server.request
    }

    # 信息保存到内存
    server.paint_connection_pool.append(connection)

    # 检测是否需要同步
    lesson = findLessonByLessonId(lessons=server.lessons, lesson_id=lesson_id)
    if lesson_id is not None:
        for paint_command in lesson["paint_command_pool"]:
            reply(request=server.request, data=paint_command)

    print(server.paint_connection_pool)
def concentrationFinalData(server, json_obj):
    course_id = json_obj["course_id"]
    lesson_id = json_obj["lesson_id"]
    uid = json_obj["uid"]

    # 转发给相关的用户
    connection = findConnectionByUid(connection_pool=server.lesson_connection_pool, uid=uid)
    send(connection_pool=server.paint_connection_pool, connection=connection, data=json_obj)


def studentCameraFrameData(server, json_obj):
    server.cv_server_connection[0].send(struct.pack("!i", len(json.dumps(json_obj))))
    server.cv_server_connection[0].send(json.dumps(json_obj).encode())


def createCVServerConnection(server, json_obj):
    server.cv_server_connection.append(server.request)


def sendChatContent(server, json_obj):
    lesson_id = json_obj["lesson_id"]
    uid = json_obj["uid"]
    lesson = None
    for lesson_temp in server.lessons:
        if lesson_temp["lesson_id"] == lesson_id:
            lesson = lesson_temp

    # 转发给所有课堂中的人
    for connection in server.lesson_connection_pool:
        if connection["lesson_id"] == lesson_id:
            if connection["uid"] == uid:  # 通知自己
                json_obj["command"] = TransportCmd.SendChatContent
                json_obj["chat_status"] = lesson["chat_status"]
                connection["socket"].send(struct.pack("!i", len(json.dumps(json_obj))))
                connection["socket"].send(json.dumps(json_obj).encode())
            else:  # 转发他人
                # 非禁言状态下/老师消息才转发
                if lesson["chat_status"] == ChatStatus.Free or json_obj["account_type"] == AccountType.Teacher:
                    json_obj["command"] = TransportCmd.RecvChatContent
                    connection["socket"].send(struct.pack("!i", len(json.dumps(json_obj))))
                    connection["socket"].send(json.dumps(json_obj).encode())


def chatBan(server, json_obj):
    lesson_id = json_obj["lesson_id"]

    # 刷新
    for lesson in server.lessons:
        if lesson["lesson_id"] == lesson_id:
            if lesson["chat_status"] == ChatStatus.Baned:
                lesson["chat_status"] = ChatStatus.Free
            else:
                lesson["chat_status"] = ChatStatus.Baned

    # 转发给所有课堂中的人
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    send(connection_pool=server.paint_connection_pool, connection=connection_list, data=json_obj)


def raiseHand(server, json_obj):
    lesson_id = json_obj["lesson_id"]
    student_id = json_obj["uid"]

    speech_status = getSpeechStatus(connection_pool=server.lesson_connection_pool, uid=student_id)
    if speech_status == SpeechStatus.InSpeech:
        json_obj["raise_hand_err"] = RaiseHandError.InSpeechError
    elif speech_status == SpeechStatus.Applying:
        json_obj["raise_hand_err"] = RaiseHandError.ApplyingError
    else:
        json_obj["raise_hand_err"] = RaiseHandError.NoError
        # 修改服务器内存中的状态
        setSpeechStatus(connection_pool=server.lesson_connection_pool, uid=student_id,
                        speech_status=SpeechStatus.Applying)
        # 转发给老师
        connection = findTeacherConnectionInLesson(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
        send(connection_pool=server.paint_connection_pool, connection=connection, data=json_obj)

    # 回复请求
    reply(server.request, json_obj)


def resultOfRaiseHand(server, json_obj):
    lesson_id = json_obj["lesson_id"]
    student_id = json_obj["student_id"]
    application_status = json_obj["application_status"]

    # 修改服务器内存中的状态
    if application_status == ApplicationStatus.Accepted:
        setSpeechStatus(connection_pool=server.lesson_connection_pool, uid=student_id,
                        speech_status=SpeechStatus.InSpeech)
    elif application_status == ApplicationStatus.Refused:
        setSpeechStatus(connection_pool=server.lesson_connection_pool, uid=student_id,
                        speech_status=SpeechStatus.SpeechFree)

    # 转发给所有课堂中的人
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    send(connection_pool=server.paint_connection_pool, connection=connection_list, data=json_obj)


def removeMemberFromInSpeech(server, json_obj):
    lesson_id = json_obj["lesson_id"]
    student_id = json_obj["student_id"]

    # 修改服务器内存中的状态
    setSpeechStatus(connection_pool=server.lesson_connection_pool, uid=student_id,
                    speech_status=SpeechStatus.SpeechFree)
    # 给所有课堂中的人发送信息
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    send(connection_pool=server.paint_connection_pool, connection=connection_list, data=json_obj)


def quitLesson(server, json_obj):
    lesson_id = json_obj["lesson_id"]
    uid = json_obj["uid"]

    # 给所有课堂中的人发送信息
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    send(connection_pool=server.paint_connection_pool, connection=connection_list, data=json_obj)

    # 删除该Connection
    removeConnectionByUid(connection_pool=server.lesson_connection_pool, uid=uid)
    removeConnectionByUid(connection_pool=server.paint_connection_pool, uid=uid)
