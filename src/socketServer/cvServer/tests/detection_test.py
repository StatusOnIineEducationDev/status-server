import cv2

from src.socketServer.cvServer.server.service.conc import detect

if __name__ == '__main__':
    # 测试
    cap = cv2.VideoCapture(0)
    concentration_score = 60
    face_orientation_result = 0.0

    # 累计
    emotion_arr = [0, 0, 0, 0, 0, 0, 0]
    blink_times = 0
    yawn_times = 0
    count = 0

    # 循环获取图像，处理图像
    while cap.isOpened():
        # 读取一帧图像
        judge, image = cap.read()
        if not judge:  # 读取图像失败
            print('摄像头读取图像失败......')
            continue

        conc_score = detect(img=image, uid='1', course_id='1', lesson_id='1', timestamp=213)
        print(conc_score)

        cv2.imshow("Output", image)
        key = cv2.waitKey(50)
        if key == ord('q'):
            break
