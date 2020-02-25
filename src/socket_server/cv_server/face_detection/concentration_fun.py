import cv2
import time
import dlib
import math
from imutils import face_utils
from scipy.spatial import distance as dist
import tensorflow as tf
import numpy as np
import random


class LoadFile:
    # 【 OpenCV函数 】
    FACE_URL = "../face_detection/data/shape_predictor_68_face_landmarks.dat"
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(FACE_URL)

    # 【表情识别】
    cascPath = "../face_detection/data/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)

    # 【疲劳检测】
    SAVE_PATH = "../face_detection/data/saved_model"

    def Initialize(SAVE_PATH):
        '''
        returns: a session with loaded graph
        '''
        sess = tf.Session()
        loader = tf.train.import_meta_graph(SAVE_PATH + '.meta')
        loader.restore(sess, SAVE_PATH)
        return sess

    # 加载模型
    sess = Initialize(SAVE_PATH)


# 连续10次获取特征点失败，表明面部朝向严重偏离
get_image_points_fail_max_time = 20
# 对应表情在数组中的下标
emotions_index = {"angry": 0, "disgust": 1, "fear": 2, "happy": 3, "sad": 4, "surprise": 5, "neutral": 6}
# emotion_labels = ['生气', '厌恶', '恐惧', '快乐', '伤心', '惊讶', '中性']
# 面部权重2.0
emotions_power = [0.059785, 0.027026, 0.039953, 0.368842, 0.059785, 0.260724, 0.183885]

# 【 头部姿态参数 】
POINTS_NUM_LANDMARK = 68
head_horizontal_rotation_angle = 0
head_vertical_rotation_angle = 0

# 【 眼部特征参数 】
EYE_AR_THRESH = 0.22  # EAR阈值
EYE_AR_CONSEC_FRAMES = 1  # 当EAR小于阈值时，接连多少帧一定发生眨眼动作

# # 对应特征点的序号
# RIGHT_EYE_START = 37 - 1
# RIGHT_EYE_END = 42 - 1
# LEFT_EYE_START = 43 - 1
# LEFT_EYE_END = 48 - 1

eye_frame_counter = 0  # 连续帧计数
blink_counter = 0  # 眨眼计数

MOUTH_AR_THRESH = 0.2
MOUTH_AR_CONSEC_FRAMES = 2

mouth_frame_counter = 0  # 连续帧计数
yawn_counter = 0

# 【 表情识别参数 】
emotion_labels = ['angry', "disgust", 'fear', 'happy', 'sad', 'surprise', 'neutral']


# emotion_labels = ['生气', '厌恶', '恐惧', '快乐', '伤心', '惊讶', '中性']

# 功  能：找到det元组中最大面部图像的标记的下标
# 参  数：det数组
# 返回值：最大标记下标
# 应  用：【头部姿态评估】
def get_largest_face_index(det):
    if len(det) == 1:
        return 0

    # 计算每组标记的面积
    face_size_area = [(detT.right() - detT.left()) * (detT.top() - detT.bottom()) for detT in det]
    max_index = 0
    max_area = face_size_area[max_index]
    for index in range(1, len(face_size_area)):
        if face_size_area[index] > max_area:
            max_area = face_size_area[index]
            max_index = index

    return max_index


# 功  能：获取面部特征点
# 参  数：图片
# 返回值：是否成功，6个特征点，左眼特征点，右眼特征点，嘴部特征点
def get_face_points(gray):
    # gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )  # 灰化

    dets = LoadFile().detector(gray, 0)

    if 0 == len(dets):
        # print("ERROR: found no face")
        return False, None, None, None, None
    largest_index = get_largest_face_from_dets(dets)
    face_rectangle = dets[largest_index]

    landmark_shape = LoadFile().predictor(gray, face_rectangle)

    return get_image_points_from_landmark_shape(landmark_shape)


# 功  能：从dlib的检测结果抽取姿态估计需要的点坐标
# 参  数：特征点数组
# 返回值：是否成功，6个特征点，左眼特征点，右眼特征点，嘴部特征点
def get_image_points_from_landmark_shape(landmark_shape):
    if landmark_shape.num_parts != POINTS_NUM_LANDMARK:
        # print(landmark_shape)
        return False, None

    # 选择6个特征点
    image_points = np.array([
        (landmark_shape.part(30).x, landmark_shape.part(30).y),  # 鼻尖
        (landmark_shape.part(8).x, landmark_shape.part(8).y),  # 下巴
        (landmark_shape.part(36).x, landmark_shape.part(36).y),  # 右眼左角
        (landmark_shape.part(45).x, landmark_shape.part(45).y),  # 左眼右角
        (landmark_shape.part(48).x, landmark_shape.part(48).y),  # 右嘴角
        (landmark_shape.part(54).x, landmark_shape.part(54).y)  # 左嘴角
    ], dtype="double")

    left_eye_points = np.array([
        (landmark_shape.part(42).x, landmark_shape.part(42).y),
        (landmark_shape.part(43).x, landmark_shape.part(43).y),
        (landmark_shape.part(44).x, landmark_shape.part(44).y),
        (landmark_shape.part(45).x, landmark_shape.part(45).y),
        (landmark_shape.part(46).x, landmark_shape.part(46).y),
        (landmark_shape.part(47).x, landmark_shape.part(47).y)
    ], dtype="double")

    right_eye_points = np.array([
        (landmark_shape.part(36).x, landmark_shape.part(36).y),
        (landmark_shape.part(37).x, landmark_shape.part(37).y),
        (landmark_shape.part(38).x, landmark_shape.part(38).y),
        (landmark_shape.part(39).x, landmark_shape.part(39).y),
        (landmark_shape.part(40).x, landmark_shape.part(40).y),
        (landmark_shape.part(41).x, landmark_shape.part(41).y)
    ], dtype="double")

    mouth_points = np.array([
        (landmark_shape.part(48).x, landmark_shape.part(48).y),
        (landmark_shape.part(54).x, landmark_shape.part(54).y),
        (landmark_shape.part(61).x, landmark_shape.part(61).y),
        (landmark_shape.part(62).x, landmark_shape.part(62).y),
        (landmark_shape.part(63).x, landmark_shape.part(63).y),
        (landmark_shape.part(65).x, landmark_shape.part(65).y),
        (landmark_shape.part(66).x, landmark_shape.part(66).y),
        (landmark_shape.part(67).x, landmark_shape.part(67).y)
    ], dtype="double")

    return True, image_points, left_eye_points, right_eye_points, mouth_points


# 功  能：获取最大的人脸
# 参  数：下标数组
# 返回值：最大值下标
def get_largest_face_from_dets(dets):
    if len(dets) == 1:
        return 0

    face_areas = [(det.right() - det.left()) * (det.bottom() - det.top()) for det in dets]

    largest_area = face_areas[0]
    largest_index = 0
    for index in range(1, len(dets)):
        if face_areas[index] > largest_area:
            largest_index = index
            largest_area = face_areas[index]

    return largest_index


# 功  能：计算头部的左右转角和抬低头转角
# 参  数：面部的6个特征点数组，图像分辨率
# 返回值：评估是否成功，左右转角，抬低头转角
# 应  用：【头部姿态评估】
def get_horizontal_and_vertical_rotor_angle(six_image_points, image_size):
    judge, rotation_vector, translation_vector = get_pose_estimation(six_image_points, image_size)
    if not judge:
        return False, -1, -1
    # 计算欧拉角
    pitch, yaw, roll = get_euler_angle(rotation_vector)

    return True, pitch, yaw, roll


# 功  能：获取姿态评估
# 参  数：特征点数组，图像分辨率
# 返回值：计算是否成功，旋转向量，翻转向量
# 应  用：【头部姿态评估】
def get_pose_estimation(six_image_points, image_size):
    # 3D模型的特征点
    ThreeD_model_points = np.array([
        (0.0, 0.0, 0.0),  # 鼻尖
        (0.0, -330.0, -65.0),  # 下巴
        (-225.0, 170.0, -135.0),  # 左眼左角
        (225.0, 170.0, -135.0),  # 右眼右角
        (-150.0, -150.0, -125.0),  # 左嘴角
        (150.0, -150.0, -125.0)  # 右嘴角
    ])

    # 根据图片计算相机参数
    focal_length = image_size[1]
    center = (image_size[1] / 2, image_size[0] / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    dist_coeffs = np.zeros((4, 1))
    # print("…………………………")
    # print("ThreeD_model_points:")
    # print(ThreeD_model_points)
    # print("six_image_points:")
    # print(six_image_points)
    judge, rotation_vector, translation_vector = cv2.solvePnP(ThreeD_model_points, six_image_points, camera_matrix,
                                                              dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

    return judge, rotation_vector, translation_vector


# 功  能：计算欧拉角
# 参  数：旋转向量
# 返回值：Y，X，Z三个旋转角
# 应  用：【头部姿态评估】
def get_euler_angle(rotation_vector):
    # 计算旋转角度
    theta = cv2.norm(rotation_vector, cv2.NORM_L2)

    # 转换为四元数
    w = math.cos(theta / 2)
    x = math.sin(theta / 2) * rotation_vector[0][0] / theta
    y = math.sin(theta / 2) * rotation_vector[1][0] / theta
    z = math.sin(theta / 2) * rotation_vector[2][0] / theta

    ysqr = y * y
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + ysqr)
    pitch = math.atan2(t0, t1)

    t2 = 2.0 * (w * y - z * x)
    if t2 > 1.0:
        t2 = 1.0
    if t2 < -1.0:
        t2 = -1.0
    yaw = math.asin(t2)

    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (ysqr + z * z)
    roll = math.atan2(t3, t4)

    # 单位转换：将弧度转换为度
    Y = int((pitch / math.pi) * 180)
    X = int((yaw / math.pi) * 180)
    Z = int((roll / math.pi) * 180)

    return Y, X, Z


# 功  能：闭眼检测和哈欠检测
# 参  数：左特征点数组，右特征点数组，嘴部特征点数组
# 返回值：是否闭眼，是否哈欠
# 应  用：【疲劳度检测】
def close_eyes_and_yawn_text(left_eye_points, right_eye_points, mouth_points):
    # 计算眼睛闭合度
    R1 = (get_two_points_distance(left_eye_points[1], left_eye_points[5]) + get_two_points_distance(left_eye_points[2],
                                                                                                    left_eye_points[
                                                                                                        4])) / get_two_points_distance(
        left_eye_points[0], left_eye_points[3]) / 2
    R2 = (get_two_points_distance(right_eye_points[1], right_eye_points[5]) + get_two_points_distance(
        right_eye_points[2], right_eye_points[4])) / get_two_points_distance(right_eye_points[0],
                                                                             right_eye_points[3]) / 2
    R1 = min(R1, R2)
    judge_eye_clase = False
    if R1 <= EYE_AR_THRESH:
        judge_eye_clase = True

    R2 = (get_two_points_distance(mouth_points[2], mouth_points[7]) + get_two_points_distance(mouth_points[3],
                                                                                              mouth_points[
                                                                                                  6]) + get_two_points_distance(
        mouth_points[5], mouth_points[4])) / get_two_points_distance(mouth_points[0], mouth_points[1]) / 3
    judge_yawn = False
    if R2 >= 0.17:
        judge_yawn = True
    # print("R1:{}   R2:{}".format(R1,R2))
    return judge_eye_clase, judge_yawn


# 功  能：计算2点距离
# 参  数：点1坐标，点2坐标
# 返回值：距离
# 应  用：【疲劳度检测】
def get_two_points_distance(point1, point2):
    distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    return distance


# 功  能：检测各个表情的概率
# 参  数：灰化图像，文件库对象
# 返回值：概率数组
# 应  用：【表情识别】
def predict_emotion(face_image_gray, loadFile):  # a single cropped face
    # print("face_image_gray:{}".format(face_image_gray))
    resized_img = cv2.resize(face_image_gray, (48, 48), interpolation=cv2.INTER_AREA)

    # cv2.imwrite(str(index)+'.png', resized_img)
    ## image = resized_img.reshape(1, 1, 48, 48)
    pixel = np.zeros((48, 48))
    for i in range(48):
        for j in range(48):
            pixel[i][j] = resized_img[i][j]
    list = Predict(pixel, loadFile.sess)
    return list


# 功  能：识别表情
# 参  数：灰化图像，文件库对象
# 返回值：空
# 应  用：【表情识别】
def face(gray, loadFile):
    global emotions_num, emotions_index
    # 灰化
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, 1)

    # faces是图像中人脸区域的数组集合
    faces = loadFile.faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # emotions_num = {"angry":0, "disgust":0, "fear":0, "happy":0, "sad":0, "surprise":0, "neutral":0}
    list1 = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    # list1 = ['生气', '厌恶', '恐惧', '快乐', '伤心', '惊讶', '中性']

    # [取最大区域方法]
    # 取faces中人脸区域最大的一个
    # (x, y, w, h) = (0,0,0,0)
    # for (xtemp,ytemp,wtemp,htemp) in faces:
    #     if wtemp*htemp>w*h:
    #         (x, y, w, h) = (xtemp,ytemp,wtemp,htemp)
    #
    # face_image_gray = gray[y:y + h, x:x + w]
    # cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # list2 = predict_emotion(face_image_gray,loadFile)
    #
    # if w*h>0:
    #     return True,emotions_index[list1[np.argmax(list2)]]
    # else:
    #     return False,-1

    for (x, y, w, h) in faces:
        face_image_gray = gray[y:y + h, x:x + w]
        cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)
        list2 = predict_emotion(face_image_gray, loadFile)

        emotions_index_result = emotions_index[list1[np.argmax(list2)]]
        if emotions_index_result is None:
            continue
        else:
            return True, emotions_index[list1[np.argmax(list2)]]
    return False, None

    # [初始代码]
    # for (x, y, w, h) in faces:
    #     face_image_gray = gray[y:y + h, x:x + w]
    #     cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #     list2 = predict_emotion(face_image_gray,loadFile)
    #
    #     emotions_num[emotions_index[list1[np.argmax(list2)]]] += 1
    #     cv2.putText(gray, list1[np.argmax(list2)], (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


##############################
# 【【【表情识别】】】
##############################
IMAGE_SIZE = 48
CLIPED_SIZE = 42
EMO_NUM = 7
NUM_CHANNEL = 1


def GetSymmetric(pixel, size):
    count = pixel.shape[0]
    sym = np.zeros((count, size, size, NUM_CHANNEL))
    for i in range(count):
        for j in range(size):
            for k in range(size):
                sym[i, j, k, 0] = pixel[i, j, size - k - 1, 0]
    return sym


def GetClippedImage(pixel, start):
    count = pixel.shape[0]
    out = np.zeros((count, CLIPED_SIZE, CLIPED_SIZE, NUM_CHANNEL))
    for i in range(count):
        for j in range(CLIPED_SIZE):
            out[i, j, :, 0] = pixel[i, start[0] + j, start[1]:start[1] + CLIPED_SIZE, 0]
    return out


def DataPreprocess(pixel):
    a = random.randint(0, 2)
    b = random.randint(3, 5)
    c = random.randint(0, 2)
    d = random.randint(3, 5)
    pixel1 = GetClippedImage(pixel, (a, c))
    pixel2 = GetClippedImage(pixel, (a, d))
    pixel3 = GetClippedImage(pixel, (b, c))
    pixel4 = GetClippedImage(pixel, (b, d))
    out_p = np.concatenate((pixel1, pixel2, pixel3, pixel4), axis=0)
    return out_p


def Predict(pixel, sess):
    max = pixel.max() + 0.001
    for i in range(IMAGE_SIZE):
        pixel[i] = pixel[i] / max
    pixel = pixel.reshape((1, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNEL))
    in_data = DataPreprocess(pixel)
    in_data = np.concatenate((in_data, GetSymmetric(in_data, CLIPED_SIZE)), axis=0)
    loaded_graph = tf.get_default_graph()
    load_x = loaded_graph.get_tensor_by_name('INPUT:0')
    load_y = loaded_graph.get_tensor_by_name('LABEL:0')
    load_log = loaded_graph.get_tensor_by_name('LOGITS:0')
    load_keep = loaded_graph.get_tensor_by_name('KEEP:0')
    logit = sess.run(load_log, feed_dict={
        load_x: in_data, load_y: np.zeros((8, EMO_NUM)), load_keep: 1.0
    })
    log = np.zeros((1, EMO_NUM))
    for i in range(8):
        log += logit[i]
    log = sess.run(tf.nn.softmax(log))
    return log
