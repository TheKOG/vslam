import cv2
import socket
import pickle
import struct
import time

def connect_to_server(server_ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((server_ip, port))
            print(f"连接到 {server_ip}:{port}...")
            return client_socket
        except ConnectionRefusedError:
            print("连接被拒绝，正在尝试重新连接...")
            time.sleep(2)

def main():
    cap = cv2.VideoCapture(9)

    # 获取摄像头的原始分辨率
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 设置新的分辨率（横向分辨率翻倍，纵向保持不变）
    new_width = original_width * 2
    new_height = original_height

    # 设置新的分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)

    server_ip = 'frp-fox.top'
    port = 53450
    server_ip = '192.168.231.61'
    port = 12345

    client_socket = connect_to_server(server_ip, port)

    # 初始化计时器
    start_time = time.time()
    interval = 0.02  # 0.02秒间隔

    # 图片计数
    count = 1

    while True:
        ret, frame = cap.read()
        # cv2.imshow('Camera', frame)

        # 当间隔时间超过0.2秒时，发送当前帧到接收端
        current_time = time.time()
        if current_time - start_time >= interval:
            try:
                # 将帧序列化为二进制数据
                data = pickle.dumps(frame)

                # 将数据的长度打包并发送给服务器
                message_size = struct.pack("!L", len(data))
                client_socket.sendall(message_size + data)

                print(f'Sent frame {count}')
                count += 1
                start_time = current_time
            except (ConnectionResetError, BrokenPipeError):
                print("连接中断，正在尝试重新连接...")
                client_socket = connect_to_server(server_ip, port)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    client_socket.close()

if __name__ == "__main__":
    main()
