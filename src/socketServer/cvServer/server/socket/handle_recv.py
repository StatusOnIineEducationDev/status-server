from src.socketServer.cvServer.server.service.conc import handleSingleFrame, detectConc
from src.edu import TransportCmd
from src.socketServer.cvServer.server.socket.socket_utils import send
from src.socketServer.utils.base64Decode import base64ToImg


def handleRecvData(conn, json_obj):
    """ 处理接收到的数据包

        根据数据包中command不同
        作出相应的处理
    :param conn: socket连接
    :param json_obj: 数据包中的json格式数据
    :return:
    """
    command = json_obj["command"]

    if command is TransportCmd.StudentCameraFrameData:
        studentCameraFrameData(conn, json_obj)


def studentCameraFrameData(conn, json_obj):
    """ 处理主服务器发送过来的帧数据

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
        conc_score = detectConc(json_obj['uid'])

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


def lessonEndHandleFunction(conn, json_obj):
    """

    :param conn:
    :param json_obj:
    :return:
    """
    pass
