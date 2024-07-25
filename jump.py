import cv2 as cv
import subprocess
import time

sn = 'LNG0224625004219'
# 0连续走 1调试 2单步
debug = 2
index = 0


def adb_long_press(duration):
    """
    执行ADB长按命令
    :param duration: 长按的时间长度，单位毫秒
    """
    adb_command = f"adb -s {sn} shell input swipe 100 100 100 100 {duration}"
    print("执行:" + adb_command)
    subprocess.run(adb_command, shell=True)


def run():
    img_path = "Ascreenshot" + str(index) + ".png"
    if debug == 0:
        # 执行 adb 命令进行截图
        subprocess.run(['adb', '-s', sn, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
        # 将截图拉取到本地
        subprocess.run(['adb', '-s', sn, 'pull', '/sdcard/screenshot.png', img_path])
    elif debug == 1:
        # 8 22
        img_path = "Ascreenshot0.png"

    img = cv.imread(img_path)
    player_template = cv.imread('player.png')
    player = cv.matchTemplate(img, player_template, cv.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(player)

    # 计算 player 的 外框
    corner_loc = (max_loc[0] + 110, max_loc[1] + 240)
    # 计算 player 的起点坐标
    player_spot = (max_loc[0] + 55, max_loc[1] + 240)

    # 画 player 的起点
    cv.circle(img, player_spot, 10, (0, 255, 255), -1)
    # cv.rectangle(img, max_loc, corner_loc, (0, 0, 255), 5)

    img_blur = cv.GaussianBlur(img, (5, 5), 0)  # 高斯模糊
    canny_img = cv.Canny(img_blur, 1, 10)  # 边缘检测

    # 去除自己 及 头上的数字
    for y in range(max_loc[1] - 100, max_loc[1] + 250):
        for x in range(max_loc[0], max_loc[0] + 110):
            canny_img[y][x] = 0

    # cv.namedWindow('img', cv.WINDOW_KEEPRATIO)
    # cv.imshow("img", canny_img)

    height, width = canny_img.shape
    crop_img = canny_img[600:int(height / 2 - 50), 0:width]
    # cv.namedWindow('img', cv.WINDOW_KEEPRATIO)
    # cv.imshow("img", crop_img)

    crop_h, crop_w = crop_img.shape
    center_x, center_y = 0, 0

    max_x = 0

    for y in range(crop_h):
        for x in range(crop_w):
            if crop_img[y, x] == 255:
                if center_x == 0:
                    center_x = x
                if x > max_x:
                    center_y = y
                    max_x = x

    cv.circle(crop_img, (center_x, center_y), 10, 255, -1)

    if debug == 1:
        cv.namedWindow('img', cv.WINDOW_KEEPRATIO)
        cv.imshow("img", crop_img)

    des_spot = (center_x, center_y + 600)
    cv.circle(img, des_spot, 10, (0, 255, 255), -1)

    cv.line(img, player_spot, des_spot, (255, 0, 0), 10)

    length = int(pow(pow(des_spot[0] - player_spot[0], 2) + pow(des_spot[1] - player_spot[1], 2), 0.5))
    print("length:%d", length)

    time = int(length * 1.15)

    if debug == 0 or debug == 2:
        adb_long_press(time)

    if debug == 2:
        cv.namedWindow('img', cv.WINDOW_KEEPRATIO)
        cv.imshow("img", img)

    if debug == 1 or debug == 2:
        cv.waitKey(0)
        cv.destroyAllWindows()


while True:
    # if debug == 2:
    #     user_input = input("请输入一些文字，或者输入'q'退出循环: ")
    #     if user_input == 'q':
    #         break

    # 保存历史图
    # index += 1
    run()
    time.sleep(2)
