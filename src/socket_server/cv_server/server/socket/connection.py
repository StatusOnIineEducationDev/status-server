import socket
import json
import time
import _thread

from src.socket_server.cv_server.conf.conf import HOST, PORT
from src.edu import TransportCmd
from src.socket_server.cv_server.server.socket.handle_recv import handleRecvData
from src.socket_server.cv_server.server.socket.socket_utils import send


def connect():
    """ 建立与主服务器的连接

        客户端把图像信息发送到主服务器
        之后再转发到这里
    :return:
    """
    # 建立与主服务器的连接
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))
    request_data = {
        "command": TransportCmd.CreateCVServerConnection
    }
    send(conn, request_data)

    # 心跳机制
    _thread.start_new_thread(keepAlive, (conn,))
    # 开始循环监听
    _thread.start_new_thread(recv, (conn,))


def recv(conn):
    """ 循环监听接收信息

    :param conn: socket连接
    :return:
    """
    # 需要指定recv_bytes为byte数组类型
    # 否则之后无法对指定字节进行分割处理
    recv_bytes = bytes()
    pack_len = -1

    # 开始监听，双循环结构
    # 外层循环负责接收字节流放入缓冲区recv_bytes
    # 内层循环负责解析缓冲区中的字节流，直至处理完缓冲区中的数据再重新返回外循环接收数据
    #
    # 另外，由于这是两个python服务端之间通信，未出现多写入包头的情况，因此包结构如下
    # ------------------------------------------
    # |   DATA_LEN (4 BYTES)   |      DATA     |
    # ------------------------------------------
    while True:
        recv_bytes += conn.recv(1024)
        # 解析过程可归结如下：
        # ①检查上一个数据包是否已解析完毕（通过pack_len控制，pack_len表示当前包体数据长度，
        #   非负数代表未解析完毕），如果已解析完，则进入下一步；否则退出内循环
        # ②检查缓冲区中数据长度是否足够4字节，若足够则进入下一步；否则退出内循环
        # ③从缓冲区中取出前4字节（一个完整数据包的头部），解析得知接下来需要接收的字节数pack_len
        # ④检查缓冲区中数据长度是否足够pack_len长度的字节数，足够则进入下一步；否则退出内循环
        # ⑤从缓冲区中取出前pack_len个字节进行解析，完成后重置pack_len,返回①
        while True:
            if len(recv_bytes) >= 4 and pack_len == -1:
                pack_len_bytes = recv_bytes[:4]
                pack_len = int.from_bytes(pack_len_bytes, 'big')
                recv_bytes = recv_bytes[4:]

            if len(recv_bytes) >= pack_len != -1:
                json_obj_bytes = recv_bytes[:pack_len]
                json_obj = json.loads(json_obj_bytes)
                recv_bytes = recv_bytes[pack_len:]
                pack_len = -1

                handleRecvData(conn, json_obj)

            if len(recv_bytes) < 4 or pack_len != -1:
                break


def keepAlive(conn):
    """ 定时（5秒）向主服务器发送一个心跳包

    :param conn: socket连接
    :return:
    """
    request_data = {
        "command": TransportCmd.KeepAlive
    }
    while True:
        send(conn, request_data)
        time.sleep(5)






