from src.socketServer.cvServer.face_detection.interface import concentration_main, concentration_calculation
from src.socketServer.cvServer.server.redis_proj_utils import RedisForDetails, RedisForConc
from src.socketServer.utils.mysqlDb import createMysqlConnection


def handleSingleFrame(img, uid, course_id, lesson_id, timestamp):
    """ 通过图像得出专注度得分

        若可以计算专注度，即返回True
    :param img: 图像矩阵
    :param uid: 用户唯一标识
    :param course_id: 课程唯一标识
    :param lesson_id: 课程下课堂唯一标识
    :param timestamp: 该帧图像的截取时间戳
    :return:
    """
    is_full = False

    is_succeed, emotion_index, is_blinked, is_yawned, h_angle, v_angle = concentration_main(img)

    redis_details = RedisForDetails()
    redis_details.addDetail(is_succeed=is_succeed, uid=uid, course_id=course_id,
                            lesson_id=lesson_id, timestamp=timestamp, emotion=emotion_index,
                            is_blinked=is_blinked, is_yawned=is_yawned, h_angle=h_angle, v_angle=v_angle)
    if is_succeed:
        is_full = redis_details.addUsefulDetail(is_succeed=is_succeed, uid=uid, course_id=course_id,
                                                lesson_id=lesson_id, timestamp=timestamp,
                                                emotion=emotion_index,
                                                is_blinked=is_blinked, is_yawned=is_yawned, h_angle=h_angle,
                                                v_angle=v_angle)

    return is_full, is_succeed, emotion_index


def detectConc(uid):
    """ 计算专注度得分

    :param uid: 用户唯一标识
    :return:
    """
    redis_conc = RedisForConc()
    redis_details = RedisForDetails()
    data_list = redis_details.getUsefulDetails(uid)

    emotion_arr = [0, 0, 0, 0, 0, 0, 0]
    blink_times = 0
    yawn_times = 0
    h_angle = 0
    v_angle = 0
    for record_data in data_list:
        # emotion保存的是表情数组的下标，以此作为arr下标，其元素加1即可
        # 至于python中的bool类型，在与int作运算时，True和False会强制转换为1和0
        emotion_arr[record_data['emotion']] += 1
        blink_times += record_data['is_blinked']
        yawn_times += record_data['is_yawned']
        h_angle = record_data['h_angle']
        v_angle = record_data['v_angle']
    conc_score = concentration_calculation(emotion_arr=emotion_arr, close_eye_time=blink_times,
                                           yawn_time=yawn_times, head_horizontal_rotation_angle=h_angle,
                                           head_vertical_rotation_angle=v_angle, frequency=10)

    redis_conc.addConcRecord(uid=uid, course_id=data_list[0]['course_id'],
                             lesson_id=data_list[0]['lesson_id'],
                             begin_timestamp=data_list[0]['timestamp'],
                             end_timestamp=data_list[-1]['timestamp'],
                             conc_score=conc_score)

    return conc_score


def dumpToMysql(lesson_id):
    """ 把专注度数据转储到mysql中

    :param lesson_id: 课程下课堂唯一标识
    :return:
    """
    mysql_cursor = createMysqlConnection().cursor()

    redis_conc = RedisForConc()
    data_list = redis_conc.getConcRecords(lesson_id)

    # 这里采取的是同时执行多条的sql指令
    # executemany效率更高
    val_list = []
    for record_data in data_list:
        # 注意里面必须是元组
        val_list.append((record_data['course_id'],
                         record_data['lesson_id'],
                         record_data['uid'],
                         record_data['conc_score'],
                         record_data['begin_timestamp'],
                         record_data['end_timestamp']))

    sql = "INSERT INTO " \
          "monitoring_record (course_id, lesson_id, uid, concentration_value, begin_timestamp, end_timestamp) " \
          "VALUES (%s, %s, %s, %s, %s, %s)"
    mysql_cursor.executemany(sql, val_list)
