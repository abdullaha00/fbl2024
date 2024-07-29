import socket
import threading
import cv2
import time
import numpy as np

# データ受け取り用の関数

dist = 20 

f = False
def udp_receiver():
        global battery_text
        global time_text
        global status_text
        global dist
        while True: 
            try:
                data, server = sock.recvfrom(1518)
                resp = data.decode(encoding="utf-8").strip()
                # レスポンスが数字だけならバッテリー残量
                if resp.isdecimal():    
                    battery_text = "Battery:" + resp + "%"
                # 最後の文字がsなら飛行時間 
                elif resp[-1:] == "s":
                    time_text = "Time:" + resp
                else: 
                    status_text = "Status:" + resp
            except:
                pass

# 問い合わせ
def ask():
    while True:
        try:
            sent = sock.sendto('battery?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)

        try:
            sent = sock.sendto('time?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)


# 離陸r
def takeoff():
        print("-----")
        try:
            sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 着陸
def land():
        try:
            sent = sock.sendto('land'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 上昇(20cm)
def up():
        try:
            sent = sock.sendto('up 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 下降(20cm)
def down():
        try:
            sent = sock.sendto('down 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 前に進む(0cm)
# def forward():
#         try:
#             print(f"moving forward by distance {dist}")
#             sent = sock.sendto(f'forward {dist}'.encode(encoding="utf-8"), TELLO_ADDRESS)
#         except:
#             pass
# # 後に進む(0cm)
# def back():
#         try:
#             print(f"moving backwards by distance {dist}")
#             sent = sock.sendto(f'back {dist}'.encode(encoding="utf-8"), TELLO_ADDRESS)
#         except:
#             pass
# # 右に進む(0cm)
# def right():
#         try:
#             print(f"moving backwards by distance {dist}")
#             sent = sock.sendto(f'right {dist}'.encode(encoding="utf-8"), TELLO_ADDRESS)
#         except:
#             pass
# # 左に進む(0cm)
# def left():
#         try:
#             sent = sock.sendto('left {dist}'.encode(encoding="utf-8"), TELLO_ADDRESS)
#         except:
#             pass
# # 右回りに回転(90 deg)
# def cw():
#         try:
#             sent = sock.sendto('cw 45'.encode(encoding="utf-8"), TELLO_ADDRESS)
#         except:
#             pass
# # 左回りに回転(90 deg)
# def ccw():
#         try:
#             sent = sock.sendto('ccw 45'.encode(encoding="utf-8"), TELLO_ADDRESS)
#         except:
#             pass
# # 速度変更(例：速度40cm/sec, 0 < speed < 100)

def move(dist, dir):
        try:
            sent = sock.sendto(f'{dir} {dist}'.encode(encoding="utf-8"), TELLO_ADDRESS)
       
        except:
            pass

def rotate(angle, dir,):
        try:
        
            sent = sock.sendto(f'{dir} {angle}'.encode(encoding="utf-8"), TELLO_ADDRESS)
     
        except:
            pass

def set_speed(n=100):
        try:
            sent = sock.sendto(f'speed {n}'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

def shift_dist():
     global dist
     if dist == 20:
          dist = 50
     elif dist == 50:
          dist = 100
     elif dist == 100:
          dist = 200
     elif dist == 200:
          dist=20
     print(f'set disance to {dist}')
    

# Tello側のローカルIPアドレス(デフォルト)、宛先ポート番号(コマンドモード用)
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)

# Telloからの映像受信用のローカルIPアドレス、宛先ポート番号
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'

command_text = "None"
battery_text = "Battery:"
time_text = "Time:"
status_text = "Status:"
dist=20

# キャプチャ用のオブジェクト
cap = None

# データ受信用のオブジェクト備
response = None

# 通信用のソケットを作成
# ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 自ホストで使用するIPアドレスとポート番号を設定
sock.bind(('', TELLO_PORT))

# 問い合わせスレッド起動
ask_thread = threading.Thread(target=ask)
ask_thread.setDaemon(True)
ask_thread.start()

# 受信用スレッドの作成
recv_thread = threading.Thread(target=udp_receiver, args=())
recv_thread.daemon = True
recv_thread.start()

# コマンドモード
sock.sendto('command'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

# カメラ映像のストリーミング開始
sock.sendto('streamon'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

if cap is None:
    cap = cv2.VideoCapture(TELLO_CAMERA_ADDRESS)

if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)
# cap = cv2.VideoCapture(0)

time.sleep(1)



cnt_frame = 0

# qrコード読み取り用のインスタンス
qcd = cv2.QRCodeDetector()


while True:
    ret, frame = cap.read()
    cnt_frame += 1

    # 動画フレームが空ならスキップ
    if frame is None or frame.size == 0:
        continue

    # カメラ映像のサイズを半分にする
    frame_height, frame_width = frame.shape[:2]
    frame_resized = cv2.resize(frame, (frame_width*4//3, frame_height*4//3))
    frame_output = frame_resized

    # qrコードの読み取り
    if cnt_frame % 5 == 0:
        retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(frame_resized) 
        if retval:
            frame_qrdet = cv2.polylines(frame_resized, points.astype(int), True, (0, 255, 0), 3)
            frame_ouput = frame_qrdet
    
        if len(decoded_info) != 0:
            print(f"読み取り結果(result)：{decoded_info}")

    
    

    # 送信したコマンドを表示
    cv2.putText(frame_output,
            text="Cmd:" + command_text,
            org=(10, 20),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # バッテリー残量を表示
    cv2.putText(frame_output,
            text=battery_text,
            org=(10, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # 飛行時間を表示
    cv2.putText(frame_output,
            text=time_text,
            org=(10, 60),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    # ステータスを表示
    cv2.putText(frame_output,
            text=status_text,
            org=(10, 80),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
            lineType=cv2.LINE_4)
    cv2.putText(frame_output,
        text=dist,
        org=(10, 100),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        color=(0, 255, 0),
        thickness=1,
        lineType=cv2.LINE_4)
    cv2.putText(frame_output,
        text=dist,
        org=(10, 120),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        color=(0, 255, 0),
        thickness=1,
        lineType=cv2.LINE_4)
    # カメラ映像を画面に表示
    cv2.imshow('Tello Camera View', frame_output)

    # キー入力を取得
    key = cv2.waitKey(1)


    match key:
        case 27: #esc
              break
        # wキーで前進
        case ord('w'):
            move(dist, 'forward')
            command_text = "Forward"
        case 2490368:
            move(2*dist, 'forward')
            command_text = "Forward (double)"
        # sキーで後進
        case ord('s'):
            move(dist, 'back')
            command_text = "Back"
        case 2621440:
            move(2*dist, 'back')
            command_text = "Backward (double)"    
        # aキーで左進
        case ord('a'):
            move(dist, 'left')
            command_text = "Left"
        case 2424832:
            move(2*dist, 'left')
            command_text = "Left (double)" 
        # dキーで右進
        case ord('a'):
            move(dist, 'right')
            command_text = "Left"
        case 2555904:
            move(2*dist, 'right')
            command_text = "Right (double)" 
        # tキーで離陸
        case ord('t'):
            takeoff()
            command_text = "Take off"
        # lキーで着陸
        case ord('l'):
            land()
            command_text = "Land"
        # rキーで上昇
        case ord('r'):
            up()
            command_text = "Up"
        # cキーで下降
        case ord('c'):
            down()
            command_text = "Down"
        # qキーで左回りに回転
        case ord('q'):
            rotate('45', 'ccw')
            command_text = "Ccw 45"
        case ord(','):
            rotate('90', 'ccw')
            command_text = "Ccw 90"
        # eキーで右回りに回転
        case ord('e'):
            rotate('45', 'cw')
            command_text = "Cw 45"
        case ord('.'):
            rotate('90', 'cw')
            command_text = "Cw 90"
        # mキーで速度変更
        case ord('m'):
            set_speed()
            command_text = "Changed speed to 100"
        case ord('1'):
            shift_dist()

cap.release()
cv2.destroyAllWindows()

# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)