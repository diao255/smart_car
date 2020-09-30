import cv2
import picture as pic
import classify as cf
import numpy as np
import signal
import sys

IS_SHOW_CV_WINDOW = True
RASPI_OS = True
if RASPI_OS:
    from SmartCarCtrl import SmartCarCtrl


width, height = 300, 300  # 设置拍摄窗口大小
x0, y0 = 200, 50  # 设置选取位置

cap = cv2.VideoCapture(0)  # 开摄像头
scc = None
if RASPI_OS:
    scc = SmartCarCtrl()


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!,car_main exit!')
    if RASPI_OS:
        scc.finalize()
    cap.release()
    cv2.destroyAllWindows()  # 关闭所有窗口
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        flag, frame = cap.read()  # 读取摄像头的内容
        if flag is False or frame is None:
            print("cap.read", flag, frame)
            continue
        frame = cv2.flip(frame, 2)
        roi, res, ret, fourier_result, efd_result = pic.binaryMask(frame, x0, y0, width, height)  # 取手势所在框图并进行处理
        if IS_SHOW_CV_WINDOW:
            cv2.imshow("roi", roi)  # 显示手势框图
            cv2.imshow("frame", frame)
            cv2.imshow("ret", ret)
        key = cv2.waitKey(1) & 0xFF  # 按键判断并进行一定的调整 # 按'q'键退出录像
        if key == ord('q'):
            break
        descirptor_in_use = abs(fourier_result)
        fd_test = np.zeros((1, 31))
        temp = descirptor_in_use[1]
        for k in range(1, len(descirptor_in_use)):
            fd_test[0, k - 1] = int(100 * descirptor_in_use[k] / temp)
        efd_test = np.zeros((1, 15))
        for k in range(1, len(efd_result)):
            temp = np.sqrt(efd_result[k][0] ** 2 + efd_result[k][1] ** 2) + np.sqrt(
                efd_result[k][2] ** 2 + efd_result[k][3] ** 2)
            efd_test[0, k - 1] = (int(1000 * temp))
        test_svm = cf.test_fd(fd_test)
        test_svm_efd = cf.test_efd(efd_test)
        print("test_svm:", test_svm[0], ", test_svm_efd:", test_svm_efd[0])
        if len(test_svm) == 0 or len(test_svm_efd) == 0:
            continue
        #
        cmd = int(test_svm)
        if RASPI_OS:
            scc.cmd_handle(cmd)

    cap.release()
    cv2.destroyAllWindows()  # 关闭所有窗口
