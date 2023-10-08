import cv2
import socket
import pickle
import struct

# 创建一个Socket连接到服务端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))

# 捕获图像
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# 将图像序列化
data = pickle.dumps(frame)
message_size = struct.pack("!L", len(data))

# 发送消息大小和图像数据到服务端
client_socket.sendall(message_size + data)

# 关闭连接
client_socket.close()
cap.release()
