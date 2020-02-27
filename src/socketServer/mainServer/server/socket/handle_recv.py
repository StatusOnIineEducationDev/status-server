import time

from src.edu import TransportCmd, CourseStatus, SpeechStatus, ChatStatus, UserStatus, AccountType
from src.socketServer.mainServer.server.services.mysql.lessonService import LessonService
from src.socketServer.mainServer.server.services.redis.rCourseService import RedisForCourseStatus, RedisForCourse
from src.socketServer.mainServer.server.services.redis.rLessonService import RedisForLessonStatus, RedisForInLesson
from src.socketServer.mainServer.server.services.redis.rUserService import RedisForUserStatus
from src.socketServer.mainServer.server.socket.socket_utils import reply, findConnectionByLessonId, send


def handleRecvData(server, json_obj):
    """ 处理接收到的数据包

        根据数据包中command不同
        作出相应的处理
    :param server: socket服务端
    :param json_obj: 数据包中的json格式数据
    :return:
    """
    command = json_obj["command"]

    if command == TransportCmd.CreateLesson:
        handleCommandCreateLesson(server, json_obj)
    elif command == TransportCmd.JoinInLesson:
        handleCommandJoinInLesson(server, json_obj)
    elif command == TransportCmd.BeginLesson:
        handleCommandBeginLesson(server, json_obj)
    # elif command == TransportCmd.PaintCommand:
    #     paintCommand(server, json_obj)
    # elif command == TransportCmd.CreatePaintConnection:
    #     createPaintConnection(server, json_obj)
    # elif command == TransportCmd.ConcentrationFinalData:
    #     concentrationFinalData(server, json_obj)
    # elif command == TransportCmd.StudentCameraFrameData:
    #     studentCameraFrameData(server, json_obj)
    # elif command == TransportCmd.CreateCVServerConnection:
    #     createCVServerConnection(server, json_obj)
    elif command == TransportCmd.EndLesson:
        handleCommandEndLesson(server, json_obj)
    elif command == TransportCmd.SendChatContent:
        handleCommandSendChatContent(server, json_obj)
    # elif command == TransportCmd.ChatBan:
    #     chatBan(server, json_obj)
    # elif command == TransportCmd.RaiseHand:
    #     raiseHand(server, json_obj)
    # elif command == TransportCmd.ResultOfRaiseHand:
    #     resultOfRaiseHand(server, json_obj)
    # elif command == TransportCmd.RemoveMemberFromInSpeech:
    #     removeMemberFromInSpeech(server, json_obj)
    elif command == TransportCmd.QuitLesson:
        handleCommandQuitLesson(server, json_obj)
    elif command == TransportCmd.TryToJoinIn:
        handleCommandTryToJoinIn(server, json_obj)


def handleCommandCreateLesson(server, json_obj):
    """ 创建课堂

    :param server: socket服务端
    :param json_obj:|- command
                    |- account_type
                    |- course_id
                    |- course_name
                    |- uid
                    |- username
    :return:
    """
    # 检查是否可以创建课堂
    # 条件为：当前课程未开课 且 教师当前未在上课状态中
    # 若符合条件，返回新建课堂的信息
    # 若不符合，则返回正在上课的课堂信息
    course_status = RedisForCourseStatus().getCourseStatus(course_id=json_obj['course_id'])
    user_status = RedisForUserStatus().getUserStatus(uid=json_obj['uid'])
    if course_status == CourseStatus.OffLine and user_status == UserStatus.Free:
        lesson = LessonService().createLesson(course_id=json_obj['course_id'], teacher_id=json_obj['uid'])
        RedisForLessonStatus().createLesson(lesson_id=str(lesson.id))
        RedisForCourse().updateLesson(course_id=json_obj['course_id'], lesson_id=str(lesson.id))
        RedisForCourseStatus().waiting(course_id=json_obj['course_id'])
        is_succeed = True
    else:
        lesson_id = RedisForInLesson().getLessonID(uid=json_obj['uid'])
        lesson = LessonService().getLessonByLessonId(lesson_id=lesson_id)
        is_succeed = False

    # 创建结果返回
    lesson_id = 'None'
    course_id = 'None'
    course_name = 'None'
    teacher_id = 'None'
    teacher_name = 'None'
    create_timestamp = -1
    # 若返回的lesson为None
    # 即说明了课堂创建失败
    if lesson is not None:
        lesson_id = lesson.id
        course_id = lesson.course.id
        course_name = lesson.course.name
        teacher_id = lesson.teacher.id
        teacher_name = lesson.teacher.name
        create_timestamp = lesson.create_timestamp
    return_data = {
        'command': TransportCmd.CreateLesson,
        'is_succeed': is_succeed,
        'lesson_id': str(lesson_id),
        'course_id': str(course_id),
        'course_name': course_name,
        'teacher_id': str(teacher_id),
        'teacher_name': teacher_name,
        'create_timestamp': create_timestamp,
    }
    reply(server.request, return_data)

    # course_id = json_obj["course_id"]
    # course_name = json_obj["course_name"]
    # uid = json_obj["uid"]
    # account_type = json_obj["account_type"]
    # username = json_obj["username"]
    # create_timestamp = time.time()
    # lesson_id = None
    # lesson_info = None
    # in_speech_now = []
    # paint_command_pool = []
    #
    # if course_id in server.course_id_arr:
    #     pass
    # else:
    #     lesson_id = "1001"
    #     # 创建的课堂（房间）信息
    #     lesson_info = {
    #         "course_id": course_id,
    #         "course_name": course_name,
    #         "lesson_id": lesson_id,
    #         "create_timestamp": create_timestamp,
    #         "begin_timestamp": create_timestamp,
    #         "teacher_id": uid,
    #         "teacher_name": username,
    #         "course_status": CourseStatus.Waiting,
    #         "chat_status": ChatStatus.Free,
    #         "in_speech_now": in_speech_now,
    #         "paint_command_pool": paint_command_pool
    #     }
    #
    # # 长连接信息
    # connection = {
    #     "uid": uid,
    #     "account_type": account_type,
    #     "course_id": course_id,
    #     "lesson_id": lesson_id,
    #     "status": {
    #         "speech_status": SpeechStatus.InSpeech
    #     },
    #     "socket": server.request
    # }
    #
    # # 信息保存到内存
    # server.lesson_connection_pool.append(connection)
    # server.lessons.append(lesson_info)
    # server.course_id_arr.append(course_id)
    #
    # # 创建结果返回
    # return_data = {
    #     "command": TransportCmd.CreateLesson,
    #     "lesson_id": lesson_id,
    #     "course_id": course_id,
    #     "course_name": course_name,
    #     "teacher_id": uid,
    #     "teacher_name": username,
    #     "create_timestamp": create_timestamp,
    # }
    # reply(server.request, return_data)


def handleCommandTryToJoinIn(server, json_obj):
    """ 学生进入课堂前的检测

    :param server: socket服务端
    :param json_obj:|- command
                    |- account_type
                    |- uid
                    |- username
    :return:
    """
    # 当前是否在上课状态中
    # 若是，则返回正在上课的课堂的信息
    # 若不是，则直接进入选定的课堂
    user_status = RedisForUserStatus().getUserStatus(uid=json_obj['uid'])
    if user_status == UserStatus.Free:
        lesson_id = 'None'
        course_id = 'None'
        course_name = 'None'
        teacher_id = 'None'
        teacher_name = 'None'
        create_timestamp = -1
        begin_timestamp = -1

        course_status = RedisForCourseStatus().getCourseStatus(course_id=json_obj['course_id'])
        if course_status != CourseStatus.OffLine:
            course_status = RedisForCourseStatus().getCourseStatus(course_id=json_obj['course_id'])
            lesson_id = RedisForCourse().getLastlyLessonID(course_id=json_obj['course_id'])
            lesson = LessonService().getLessonByLessonId(lesson_id=lesson_id)
            RedisForInLesson().joinLesson(uid=json_obj['uid'], course_id=json_obj['course_id'], lesson_id=lesson_id)

            # 根据课堂状态调整用户当前状态
            if course_status == CourseStatus.Waiting:
                RedisForUserStatus().inRoom(uid=json_obj['uid'])
            elif course_status == CourseStatus.OnLine or course_status == CourseStatus.CantJoinIn:
                RedisForUserStatus().inClass(uid=json_obj['uid'])

            # 长连接信息存到内存连接池
            server.socket_type = 'lesson'
            conn = {
                'uid': json_obj['uid'],
                'account_type': json_obj['account_type'],
                'course_id': str(lesson.course.id),
                'lesson_id': str(lesson.id),
                'socket': server.request
            }
            # 如果该信息已经存在
            server.lesson_connection_pool.append(conn)

            lesson_id = lesson.id
            course_id = lesson.course.id
            course_name = lesson.course.name
            teacher_id = lesson.teacher.id
            teacher_name = lesson.teacher.id
            create_timestamp = lesson.create_timestamp
            begin_timestamp = lesson.begin_timestamp

        # 创建结果返回
        return_data = {
            'command': TransportCmd.JoinInLesson,
            'course_status': course_status,
            'course_id': str(course_id),
            'course_name': course_name,
            'lesson_id': str(lesson_id),
            'teacher_id': str(teacher_id),
            'teacher_name': teacher_name,
            'create_timestamp': create_timestamp,
            'begin_timestamp': begin_timestamp
        }
    else:
        # 返回正在上课的信息
        lesson_id = RedisForInLesson().getLessonID(uid=json_obj['uid'])
        lesson = LessonService().getLessonByLessonId(lesson_id=lesson_id)

        return_data = {
            'command': TransportCmd.TryToJoinIn,
            'lesson_id': str(lesson.id),
            'course_id': str(lesson.course.id),
            'course_name': lesson.course.name,
            'teacher_id': str(lesson.teacher.id),
            'teacher_name': lesson.teacher.name,
            'create_timestamp': lesson.create_timestamp,
        }

    reply(server.request, return_data)


def handleCommandJoinInLesson(server, json_obj):
    """ 加入课堂

    :param server: socket服务端
    :param json_obj:|- command
                    |- account_type
                    |- course_id
                    |- course_name
                    |- uid
                    |- username
    :return:
    """
    lesson_id = 'None'
    course_id = 'None'
    course_name = 'None'
    teacher_id = 'None'
    teacher_name = 'None'
    create_timestamp = -1
    begin_timestamp = -1

    # 先判断课程状态看是该课程是否正在上课
    course_status = RedisForCourseStatus().getCourseStatus(course_id=json_obj['course_id'])
    if course_status != CourseStatus.OffLine:
        if course_status == CourseStatus.CantJoinIn and json_obj['account_type'] == AccountType.Student:
            pass
        else:
            lesson_id = RedisForCourse().getLastlyLessonID(course_id=json_obj['course_id'])
            lesson = LessonService().getLessonByLessonId(lesson_id=lesson_id)
            RedisForInLesson().joinLesson(uid=json_obj['uid'], course_id=json_obj['course_id'],
                                          lesson_id=str(lesson_id))
            # 根据课堂状态调整用户当前状态
            if course_status == CourseStatus.Waiting:
                RedisForUserStatus().inRoom(uid=json_obj['uid'])
            elif course_status == CourseStatus.OnLine or course_status == CourseStatus.CantJoinIn:
                RedisForUserStatus().inClass(uid=json_obj['uid'])

            # 长连接信息存到内存连接池
            server.socket_type = 'lesson'
            conn = {
                'uid': json_obj['uid'],
                'account_type': json_obj['account_type'],
                'course_id': str(lesson.course.id),
                'lesson_id': str(lesson.id),
                'socket': server.request
            }
            # 如果该信息已经存在
            server.lesson_connection_pool.append(conn)

            lesson_id = lesson.id
            course_id = lesson.course.id
            course_name = lesson.course.name
            teacher_id = lesson.teacher.id
            teacher_name = lesson.teacher.name
            create_timestamp = lesson.create_timestamp
            begin_timestamp = lesson.begin_timestamp

    # 创建结果返回
    return_data = {
        'command': TransportCmd.JoinInLesson,
        'course_status': course_status,
        'course_id': str(course_id),
        'course_name': course_name,
        'lesson_id': str(lesson_id),
        'teacher_id': str(teacher_id),
        'teacher_name': teacher_name,
        'create_timestamp': create_timestamp,
        'begin_timestamp': begin_timestamp
    }
    reply(server.request, return_data)

    # course_id = json_obj["course_id"]
    # uid = json_obj["uid"]
    # account_type = json_obj["account_type"]
    # lesson_id = None
    # teacher_id = None
    # teacher_name = None
    # course_name = None
    # create_timestamp = None
    # begin_timestamp = None
    # course_status = CourseStatus.OffLine
    #
    # if course_id in server.course_id_arr:
    #     for lesson in server.lessons:
    #         if lesson["course_id"] == course_id:
    #             lesson_id = lesson["lesson_id"]
    #             course_status = lesson["course_status"]
    #             teacher_id = lesson["teacher_id"]
    #             teacher_name = lesson["teacher_name"]
    #             course_name = lesson["course_name"]
    #             create_timestamp = lesson["create_timestamp"]
    #             begin_timestamp = lesson["begin_timestamp"]
    #
    #             # 长连接信息
    #             connection = {
    #                 "uid": uid,
    #                 "account_type": account_type,
    #                 "course_id": course_id,
    #                 "lesson_id": lesson_id,
    #                 "status": {
    #                     "speech_status": SpeechStatus.SpeechFree
    #                 },
    #                 "socket": server.request
    #             }
    #             # 信息保存到内存
    #             server.lesson_connection_pool.append(connection)
    #
    # # 结果返回
    # return_info = {
    #     "command": TransportCmd.JoinInLesson,
    #     "course_status": course_status,
    #     "course_id": course_id,
    #     "course_name": course_name,
    #     "lesson_id": lesson_id,
    #     "teacher_id": teacher_id,
    #     "teacher_name": teacher_name,
    #     "create_timestamp": create_timestamp,
    #     "begin_timestamp": begin_timestamp
    # }
    # server.request.send(struct.pack("!i", len(json.dumps(return_info))))
    # server.request.send(json.dumps(return_info).encode())


def handleCommandBeginLesson(server, json_obj):
    """ 开启课堂（开始上课）

    :param server: socket服务端
    :param json_obj:|- command
                    |- account_type
                    |- timestamp
                    |- course_id
                    |- lesson_id
                    |- uid
                    |- username
    :return:
    """
    course_status = RedisForCourseStatus().getCourseStatus(course_id=json_obj['course_id'])
    if course_status == CourseStatus.Waiting:
        # 更新课程状态：waiting -> online
        lesson = LessonService().beginLesson(lesson_id=json_obj['lesson_id'])
        RedisForCourseStatus().onLine(course_id=json_obj['course_id'])
        # 给所有课堂中的人发送信息
        send_data = {
            'command': TransportCmd.BeginLesson,
            'course_id': str(lesson.course.id),
            'lesson_id': str(lesson.id),
            'begin_timestamp': lesson.begin_timestamp
        }
        connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool,
                                                   lesson_id=str(lesson.id))
        send(connection=connection_list, data=send_data)

    # course_id = json_obj["course_id"]
    # lesson_id = json_obj["lesson_id"]
    # begin_timestamp = time.time()
    #
    # # 更改课堂状态
    # lesson = findLessonByLessonId(lessons=server.lessons, lesson_id=lesson_id)
    # lesson["course_status"] = CourseStatus.OnLine
    # lesson["begin_timestamp"] = begin_timestamp
    #
    # # 给所有课堂中的人发送信息
    # send_info = {
    #     "command": TransportCmd.BeginLesson,
    #     "course_id": course_id,
    #     "lesson_id": lesson_id,
    #     "begin_timestamp": begin_timestamp
    # }
    # connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    # send(connection_pool=server.lesson_connection_pool, connection=connection_list, data=send_info)


def handleCommandEndLesson(server, json_obj):
    """ 结束课堂

    :param server: socket服务端
    :param json_obj:|- command
                    |- account_type
                    |- timestamp
                    |- course_id
                    |- lesson_id
                    |- uid
                    |- username
    :return:
    """
    # 更新课程状态：online/waiting/cantJoinIn -> offline
    lesson = LessonService().endLesson(lesson_id=json_obj['lesson_id'])
    RedisForCourseStatus().offLine(course_id=json_obj['course_id'])
    RedisForUserStatus().free(uid=json_obj['uid'])
    # 清除redis缓存
    RedisForLessonStatus().endLesson(lesson_id=lesson.id)
    uid_arr = RedisForInLesson().getLessonUsersUID(lesson_id=lesson.id)
    redis_for_in_lesson = RedisForInLesson()
    redis_for_user_status = RedisForUserStatus()
    for uid in uid_arr:
        redis_for_in_lesson.quitLesson(uid=uid)
        redis_for_user_status.free(uid=uid)

    # 给所有课堂中的人发送信息
    send_data = {
        'command': TransportCmd.EndLesson,
        'course_id': str(lesson.course.id),
        'lesson_id': str(lesson.id),
        'end_timestamp': lesson.end_timestamp
    }
    connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=str(lesson.id))
    send(connection=connection_list, data=send_data)

    # course_id = json_obj["course_id"]
    # lesson_id = json_obj["lesson_id"]
    # end_timestamp = time.time()
    #
    # # 给所有课堂中的人发送信息
    # send_info = {
    #     "command": TransportCmd.EndLesson,
    #     "course_id": course_id,
    #     "lesson_id": lesson_id,
    #     "end_timestamp": end_timestamp
    # }
    # connection_list = findConnectionByLessonId(connection_pool=server.lesson_connection_pool, lesson_id=lesson_id)
    # send(connection_pool=server.lesson_connection_pool, connection=connection_list, data=send_info)
    #
    # # 清除connection
    # for connection in server.lesson_connection_pool:
    #     if connection["lesson_id"] == lesson_id:
    #         server.lesson_connection_pool.remove(connection)
    # for connection in server.paint_connection_pool:
    #     if connection["lesson_id"] == lesson_id:
    #         server.paint_connection_pool.remove(connection)
    # for lesson in server.lessons:
    #     if lesson["lesson_id"] == lesson_id:
    #         server.lessons.remove(lesson)
    # if course_id in server.course_id_arr:
    #     server.course_id_arr.remove(course_id)


def handleCommandQuitLesson(server, json_obj):
    """ 退出课堂

    :param server: socket服务端
    :param json_obj:|- command
                    |- account_type
                    |- timestamp
                    |- course_id
                    |- lesson_id
                    |- uid
                    |- username
    :return:
    """
    # 更新用户状态
    RedisForUserStatus().free(uid=json_obj['uid'])
    # 清除redis缓存
    RedisForInLesson().quitLesson(uid=json_obj['uid'])

    # 给所有课堂中的人发送信息
    return_data = {
        'command': TransportCmd.QuitLesson,
    }
    reply(server.request, return_data)


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


def handleCommandSendChatContent(server, json_obj):
    print('2')
    # lesson_id = json_obj["lesson_id"]
    # uid = json_obj["uid"]
    # lesson = None
    # for lesson_temp in server.lessons:
    #     if lesson_temp["lesson_id"] == lesson_id:
    #         lesson = lesson_temp
    #
    # # 转发给所有课堂中的人
    # for connection in server.lesson_connection_pool:
    #     if connection["lesson_id"] == lesson_id:
    #         if connection["uid"] == uid:  # 通知自己
    #             json_obj["command"] = TransportCmd.SendChatContent
    #             json_obj["chat_status"] = lesson["chat_status"]
    #             connection["socket"].send(struct.pack("!i", len(json.dumps(json_obj))))
    #             connection["socket"].send(json.dumps(json_obj).encode())
    #         else:  # 转发他人
    #             # 非禁言状态下/老师消息才转发
    #             if lesson["chat_status"] == ChatStatus.Free or json_obj["account_type"] == AccountType.Teacher:
    #                 json_obj["command"] = TransportCmd.RecvChatContent
    #                 connection["socket"].send(struct.pack("!i", len(json.dumps(json_obj))))
    #                 connection["socket"].send(json.dumps(json_obj).encode())


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



