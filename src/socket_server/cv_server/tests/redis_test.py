from src.socket_server.cv_server.server.service.conc import dumpToMysql

if __name__ == '__main__':
    # # 测试
    # cap = cv2.VideoCapture(0)
    # conc = RedisForConc()
    # # 循环获取图像，处理图像
    # while cap.isOpened():
    #     # 读取一帧图像
    #     judge, image = cap.read()
    #     if not judge:  # 读取图像失败
    #         print('摄像头读取图像失败......')
    #         continue
    #
    #     is_succeed, emotion_index, is_blinked, is_yawned, h_angle, v_angle = concentration_main(image)
    #     conc.addDetails(uid='10001', course_id='302',
    #                     lesson_id='4021', timestamp=123123123,
    #                     emotion=emotion_index, is_blinked=is_blinked, is_yawned=is_yawned,
    #                     h_angle=h_angle, v_angle=v_angle)
    #     print(is_succeed)
    #
    #     cv2.imshow("Output", image)
    #     key = cv2.waitKey(50)
    #     if key == ord('q'):
    #         break

    dumpToMysql('1')
