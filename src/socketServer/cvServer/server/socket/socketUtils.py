import struct
import json


def send(conn, data):
    """ 给指定socket连接发送一段数据

    :param conn: socket连接
    :param data: 需要发送的数据
    :return:
    """
    # 一个完整的数据包由“包头（固定为4字节，内容为包体的长度）”以及“包体（需要发送的数据）”组成
    # -------------------------------------------------------------------
    # |   DATA_LEN (4 BYTES)   |   DATA_LEN (4 BYTES)   |      DATA     |
    # -------------------------------------------------------------------
    # 在c++客户端那里写入长度时会多出4字节（才学疏浅，不知原因），因此有了上面两个包头的结构
    # 为保持接口统一，这里人为多加4字节（发送两次头部）
    conn.send(struct.pack("!i", len(json.dumps(data))))
    conn.send(struct.pack("!i", len(json.dumps(data))))
    conn.send(json.dumps(data).encode())
