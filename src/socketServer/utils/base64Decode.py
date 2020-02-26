import base64
import numpy as np
import cv2


def base64ToImg(base64_str):
    str_decode = base64.b64decode(base64_str)
    img_mat = np.frombuffer(str_decode, np.uint8)
    img = cv2.imdecode(img_mat, cv2.IMREAD_COLOR)

    return img
