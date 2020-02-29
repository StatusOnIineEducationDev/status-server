import cv2
import numpy as np

from src.socketServer.cvServer.face_detection import concentrationFun as Fun

# 加载所需库文件
loadFile = Fun.LoadFile()
cv2 = cv2


# 功能：检测图像表情、是否眨眼、是否哈欠、头部水平（垂直）转角参数
# 参数：图像
# 返回值：无法获取特征点-False,-1,False,False,0,0
#         正常获取特征点-True,表情对应数组下标,True/False,True/False,水平转角度数,垂直转角度数
def concentration_main(image):
    # 重新调整图片规格
    size = image.shape
    if size[0] > 700:
        image_hight = size[0] / 3
        image_weight = size[1] / 3
        # 重设图像规格
        image = cv2.resize(image, (int(image_weight), int(image_hight)), interpolation=cv2.INTER_CUBIC)
        size = image.shape
    # 图像灰化
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, 1)

    # 获取面部特征点
    judge, six_image_points, left_eys_points, right_eye_points, mouth_points = Fun.get_face_points(gray)

    # 【连续获取图像特征点失败未处理】
    # 图像特征点获取成功
    if judge:
        # 计算头部的左右转头转角和抬低头转角
        judge, pitch, yaw, roll = Fun.get_horizontal_and_vertical_rotor_angle(six_image_points, size)
        if not judge:
            print("头部姿态评估失败！")
            return False, -1, False, False, 0, 0
        # else:
        #     # 计算水平转角和
        #     Fun.head_horizontal_rotation_angle += abs(yaw)
        #     # 计算垂直转角和
        #     Fun.head_vertical_rotation_angle = 180 - abs(pitch)

        # 闭眼和哈欠检测
        close_eys_judge, yawn_judge = Fun.close_eyes_and_yawn_text(left_eys_points, right_eye_points, mouth_points)

        # 表情识别
        judge, face_index = Fun.face(gray, loadFile)
        if not judge:
            return False, -1, False, False, 0, 0

        return True, face_index, close_eys_judge, yawn_judge, abs(yaw), (180 - abs(pitch))
    else:
        return False, -1, False, False, 0, 0


# 功能：模糊综合评判
# 参数：各个表情计数数组，闭眼次数，哈欠次数，头部水平（垂直）转角，每个周期的检测次数
# 返回值：专注度评分
def concentration_calculation(emotion_arr, close_eye_time, yawn_time, head_horizontal_rotation_angle,
                              head_vertical_rotation_angle, frequency):
    # 评估
    # 1.疲劳评估：1*PERCLOS + 0.8*平均闭眼时长 + 0.5*哈欠次数
    # 计算PERCLOS值
    PERCLOS_value = close_eye_time / frequency
    fatigue_assessment_result = (1 - PERCLOS_value) / 1.8 + (1 - yawn_time / frequency) * 0.8 / 1.8

    # 2.头部姿态评估：（垂直转角分值+水平转角均值）/2
    # 左（右）转头转角均值
    head_horizontal_rotation_mean_angle = head_horizontal_rotation_angle / frequency
    # 抬低头转角均值
    head_vertical_rotation_mean_angle = head_vertical_rotation_angle / frequency

    horizontal_head_score = 0
    vertical_head_score = 0
    # 计算结果
    if head_horizontal_rotation_mean_angle < 70:
        horizontal_head_score = (1 - head_horizontal_rotation_mean_angle / 70)

    if head_vertical_rotation_mean_angle < 15:
        vertical_head_score = (1 - head_vertical_rotation_mean_angle / 15)
    # 取中值
    head_pose_result = (horizontal_head_score + vertical_head_score) / 2

    # 3.表情评估
    for i in range(np.size(emotion_arr)):
        emotion_arr[i] *= Fun.emotions_power[i]
    emotions_score = sum(emotion_arr) / frequency

    # 4.总体评分
    concentration_score = 0.649118 * head_pose_result + 0.27895457 * fatigue_assessment_result + 0.07192743 * emotions_score
    # print("{}:{}".format(time.strftime("%H:%M:%S", time.localtime()), concentration_score))

    # 【调用程序还原记录数据】

    return concentration_score
