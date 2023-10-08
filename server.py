import cv2
import socket
import pickle
import struct
import stereo_depth_online
import time
import subprocess
import os

def start_server(host_ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip, port))
    server_socket.listen(5)
    print(f"监听来自 {host_ip}:{port} 的连接...")
    return server_socket

def accept_client(server_socket):
    client_socket, addr = server_socket.accept()
    print(f"接受来自 {addr[0]}:{addr[1]} 的连接")
    return client_socket

def main():
    
    with open("Stereo/data/timestamp.txt","w") as f:
        f.write("-1")
        f.close()
    subprocess.Popen(os.getcwd()+"/Stereo/stereo_euroc Stereo/ORBvoc.txt Stereo/HBV.yaml Stereo/data/left Stereo/data/right Stereo/data/timestamp.txt ", shell=True)
        
    host_ip = '192.168.231.61'  # 你的服务器IP地址
    port = 12345  # 选择一个未被占用的端口

    server_socket = start_server(host_ip, port)

    client_socket = accept_client(server_socket)

    data = b''
    payload_size = struct.calcsize("!L")

    stereo_depth_online.Init("stereoDepth/stereo_cam.yml")
    start_time=time.time()
    while True:
        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("!L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        height,width,c=frame.shape
        leftImage = frame[0:height, 0:int(width/2), :]
        rightImage = frame[0:height, int(width/2):width, :]
        disparity_image=stereo_depth_online.stereo_depth(leftImage,rightImage)
        cv2.imshow('Server Video', disparity_image)
        ct=time.time()-start_time
        cv2.imwrite("Stereo/data/left/{}.png".format(ct),leftImage)
        cv2.imwrite("Stereo/data/right/{}.png".format(ct),rightImage)
        with open("Stereo/data/timestamp.txt","w") as f:
            f.write(str(ct))
            f.close()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    client_socket.close()
    server_socket.close()
    
    with open("Stereo/data/timestamp.txt","w") as f:
        f.write("-1")
        f.close()

if __name__ == "__main__":
    main()
