import datetime

from src.socketServer.cvServer.server.models.monitoringRecord import MonitoringRecord
from src.socketServer.cvServer.server.services.mysql.monitoringRecordService import MonitoringRecordService
from src.socketServer.cvServer.server.services.other.conc import handleSingleFrame, detectConc
from src.edu import TransportCmd
from src.socketServer.cvServer.server.services.redis.rConcService import RedisForConc, RedisForDetails
from src.socketServer.cvServer.server.socket.socketUtils import send
from src.socketServer.utils.base64Decode import base64ToImg


def handleRecvData(conn, json_obj):
    """ 处理接收到的数据包

        根据数据包中command不同
        作出相应的处理
    :param conn: socket连接
    :param json_obj: 数据包中的json格式数据
    :return:
    """
    print(conn.getsockname()[0],
          ' - [' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']',
          ' RECV ',
          json_obj)
    command = json_obj["command"]

    if command == TransportCmd.StudentCameraFrameData:
        handleCommandStudentCameraFrameData(conn, json_obj)
    if command == TransportCmd.EndLesson:
        handleCommandEndLesson(conn, json_obj)


def handleCommandStudentCameraFrameData(conn, json_obj):
    """ 处理主服务器发送过来的帧数据

        is_succeed为False代表没有检测到人脸
        conc_score为-1代表未收集够有效帧
    :param conn: socket连接
    :param json_obj: 数据包
    :return:
    """
    conc_score = -1

    img = base64ToImg(base64_str=json_obj['frame_mat'])
    is_full, is_succeed, emotion = handleSingleFrame(img=img, uid=json_obj['uid'],
                                                     course_id=json_obj['course_id'],
                                                     lesson_id=json_obj['lesson_id'],
                                                     timestamp=json_obj['concentration_timestamp'])
    if is_full:
        conc_score = int(detectConc(lesson_id=json_obj['lesson_id'], uid=json_obj['uid']) * 100)  # 返回的是一个小数

    return_data = {
        'command': TransportCmd.ConcentrationFinalData,
        'is_succeed': is_succeed,
        'course_id': json_obj['course_id'],
        'lesson_id': json_obj['lesson_id'],
        'uid': json_obj['uid'],
        'concentration_value': conc_score,
        'emotion': emotion,
        'concentration_timestamp': json_obj["concentration_timestamp"]
    }
    send(conn, return_data)


def handleCommandEndLesson(conn, json_obj):
    """ 结束课堂

        需要做转储工作
    :param conn: socket连接
    :param json_obj:|- command
                    |- account_type
                    |- timestamp
                    |- course_id
                    |- lesson_id
                    |- uid
                    |- username
    :return:
    """
    # 转储
    data_list = RedisForConc().getConcRecords(json_obj['lesson_id'])
    records = []
    for record_data in data_list:
        # 注意里面必须是元组
        record = MonitoringRecord(course_id=record_data['course_id'],
                                  lesson_id=record_data['lesson_id'],
                                  uid=record_data['uid'],
                                  concentration_value=record_data['conc_score'],
                                  begin_timestamp=record_data['begin_timestamp'],
                                  end_timestamp=record_data['end_timestamp'])
        records.append(record)
    MonitoringRecordService().insertManyRecords(records)

