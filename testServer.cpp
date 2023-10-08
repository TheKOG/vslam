#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgcodecs/imgcodecs.hpp>
#include <opencv2/core/core.hpp>
#include <fstream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <cstring>
#include <cstdlib>

int main() {
    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == -1) {
        std::cerr << "Error creating socket" << std::endl;
        return -1;
    }

    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(12345);
    serverAddress.sin_addr.s_addr = INADDR_ANY;

    if (bind(serverSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) == -1) {
        std::cerr << "Error binding socket" << std::endl;
        return -1;
    }

    if (listen(serverSocket, 5) == -1) {
        std::cerr << "Error listening on socket" << std::endl;
        return -1;
    }

    std::cout << "Server listening on port " << "127.0.0.1" << std::endl;

    while (true) {
        int clientSocket = accept(serverSocket, NULL, NULL);
        if (clientSocket == -1) {
            std::cerr << "Error accepting client connection" << std::endl;
            continue;
        }

        // 接收消息大小
        uint32_t imageSize;
        ssize_t receivedBytes = recv(clientSocket, &imageSize, sizeof(imageSize), 0);
        if (receivedBytes == sizeof(imageSize)) {
            imageSize = ntohl(imageSize);
            std::vector<char> receivedData(imageSize);

            // 接收图像数据
            receivedBytes = recv(clientSocket, receivedData.data(), imageSize, 0);
            if (receivedBytes == imageSize) {
                cv::Mat receivedImage = cv::Mat(1, imageSize, CV_8U, receivedData.data());

                // 在这里可以使用receivedImage进行图像处理
                cv::imwrite("received_image.jpg", receivedImage);
                std::cout << "Received image successfully" << std::endl;
            } else {
                std::cerr << "Error receiving image data" << std::endl;
            }
        } else {
            std::cerr << "Error receiving image size" << std::endl;
        }

        close(clientSocket);
    }

    close(serverSocket);
    return 0;
}
