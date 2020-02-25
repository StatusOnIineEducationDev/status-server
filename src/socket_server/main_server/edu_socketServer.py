import socketserver
import json
import struct

from src.edu import *
from src.socket_server.main_server.edu_handleRecvFunction import *


class OnlineEducationServer(socketserver.BaseRequestHandler):
    # cv服务器连接
    cv_server_connection = []
    # 常规长连接池
    normal_connection_pool = []
    # 课堂连接池
    lesson_connection_pool = []
    # 画板同步连接池
    paint_connection_pool = []
    # 已创建的课堂
    lessons = []
    course_id_arr = []

    def handle(self):
        recv_bytes = bytes()
        pack_len = -1

        while True:
            try:
                recv_bytes += self.request.recv(1024)
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

                        self.handleRecv(json_obj)

                    if len(recv_bytes) < 8 or pack_len != -1:
                        break
            except ConnectionResetError:  # 意外断线
                break
        del self

    def handleRecv(self, json_obj):
        command = json_obj["command"]
        # print(json_obj)
        if command == TransportCmd.CreateLesson:
            createLesson(self, json_obj)
        elif command == TransportCmd.JoinInLesson:
            joinInLesson(self, json_obj)
        elif command == TransportCmd.BeginLesson:
            beginLesson(self, json_obj)
        elif command == TransportCmd.PaintCommand:
            paintCommand(self, json_obj)
        elif command == TransportCmd.CreatePaintConnection:
            createPaintConnection(self, json_obj)
        elif command == TransportCmd.ConcentrationFinalData:
            concentrationFinalData(self, json_obj)
        elif command == TransportCmd.StudentCameraFrameData:
            studentCameraFrameData(self, json_obj)
        elif command == TransportCmd.CreateCVServerConnection:
            createCVServerConnection(self, json_obj)
        elif command == TransportCmd.EndLesson:
            endLesson(self, json_obj)
        elif command == TransportCmd.SendChatContent:
            sendChatContent(self, json_obj)
        elif command == TransportCmd.ChatBan:
            chatBan(self, json_obj)
        elif command == TransportCmd.RaiseHand:
            raiseHand(self, json_obj)
        elif command == TransportCmd.ResultOfRaiseHand:
            resultOfRaiseHand(self, json_obj)
        elif command == TransportCmd.RemoveMemberFromInSpeech:
            removeMemberFromInSpeech(self, json_obj)
        elif command == TransportCmd.QuitLesson:
            quitLesson(self, json_obj)


if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 5002), OnlineEducationServer)
    print("EDU SEVER is running.")
    server.serve_forever()


