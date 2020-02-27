import socketserver
import json

from src.socketServer.mainServer.server.socket.handle_recv import handleRecvData


class OnlineEducationServer(socketserver.BaseRequestHandler):
    # cv服务器连接
    cv_server_connection = []
    # 课堂连接池
    lesson_connection_pool = []
    # 画板同步连接池
    paint_connection_pool = []

    def handle(self):
        """ 循环监听接收信息

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
            print(self.lesson_connection_pool)
            recv_bytes += self.request.recv(1024)
            # 解析过程可归结如下：
            # ①检查上一个数据包是否已解析完毕（通过pack_len控制，pack_len表示当前包体数据长度，
            #   非负数代表未解析完毕），如果已解析完，则进入下一步；否则退出内循环
            # ②检查缓冲区中数据长度是否足够4字节，若足够则进入下一步；否则退出内循环
            # ③从缓冲区中取出前4字节（一个完整数据包的头部），解析得知接下来需要接收的字节数pack_len
            # ④检查缓冲区中数据长度是否足够pack_len长度的字节数，足够则进入下一步；否则退出内循环
            # ⑤从缓冲区中取出前pack_len个字节进行解析，完成后重置pack_len,返回①
            if recv_bytes:
                while True:
                    if len(recv_bytes) >= 8 and pack_len == -1:
                        pack_len_bytes = recv_bytes[:8]
                        pack_len_bytes = pack_len_bytes[:4]
                        pack_len = int.from_bytes(pack_len_bytes, 'big')
                        recv_bytes = recv_bytes[8:]

                    if len(recv_bytes) >= pack_len != -1:
                        json_obj_bytes = recv_bytes[:pack_len]
                        json_obj = json.loads(json_obj_bytes)
                        recv_bytes = recv_bytes[pack_len:]
                        pack_len = -1

                        handleRecvData(self, json_obj)

                    if len(recv_bytes) < 8 or pack_len != -1:
                        break
            else:
                # 从连接池中找到该连接并剔除
                # 这真的是一个极其愚蠢的办法
                # 但需求至上！！！别给我整什么算法有的没的！！！
                # 没时间学！！！也没时间写！！！！！
                for conn in self.lesson_connection_pool:
                    if conn['socket'] == self.request:
                        self.lesson_connection_pool.remove(conn)
                break




