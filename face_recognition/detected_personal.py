import cv2
import numpy as np
import time
from websocket_server import WebsocketServer
import threading
import signal
import sys

# Global Variables
detected_printed = False

# SIGINTハンドラ関数
def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    server.shutdown()
    cv2.destroyAllWindows()
    sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)

# WebSocketサーバーのコールバック関数
def new_client(client, server):
    global detected_printed
    detected_printed = False
    print("New client connected")

def client_left(client, server):
    print("Client disconnected")

def message_received(client, server, message):
    print("Message received: {}".format(message))
    None



def initialize_recognizer(trainer_path, cascade_path):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print(type(recognizer))
    recognizer.read(trainer_path)
    face_cascade = cv2.CascadeClassifier(cascade_path)
    return recognizer, face_cascade

def detect_faces(gray, face_cascade, minW, minH):
    return face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )

def get_names():
    def get_file_path(folder_path):
        import os
        files = os.listdir(folder_path)
        files_file = [('{}/{}'.format(folder_path,f)) for f in files if os.path.isfile(os.path.join(folder_path, f))]
        return files_file

    import json
    names = {}
    for file in get_file_path('./dataset'):
        data = json.load(open(file))
        names[data['id']] = data['name']
    return names

def main():
    recognizer, face_cascade = initialize_recognizer('trainer.yml', 'haarcascade_frontalface_default.xml')
    font = cv2.FONT_HERSHEY_SIMPLEX
    names = get_names()
    print(names)

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    prev_id = None
    last_detected_time = None
    

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray, face_cascade, minW, minH)
        global detected_printed

        # WebSocketにインターバルを空けてメッセージを送信
        if len(faces) > 0:
            if not detected_printed:
                message = '{"isDetected" : true}'
                server.send_message_to_all(message)
                print("検出")
                detected_printed = True
            last_detected_time = time.time()
        elif last_detected_time and time.time() - last_detected_time > 5 and detected_printed:
            message = '{"isDetected" : false}'
            server.send_message_to_all(message)
            print("非検出")
            detected_printed = False
            prev_id = None

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            
            sys.stdout.write("\r")
            sys.stdout.write(f"id: {id}, name: {names[id]}, confidence: {confidence}")
            sys.stdout.flush()
            
            id_name = names[id] if confidence < 50 else "unknown"
            confidence_text = "  {0}%".format(round(100 - confidence))
            
            if prev_id == None and id_name != "unknown":
                print(f"{id_name} を認識")
                prev_id = id_name
                
            cv2.putText(img, str(id_name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, confidence_text, (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)
        time.sleep(0.1)
        if cv2.waitKey(10) & 0xff == 27:
            break

    print("プログラムを終了します。")
    cam.release()
    cv2.destroyAllWindows()
    exit(0)

# WebSocketサーバーの初期設定
server = WebsocketServer(host='localhost', port=5001)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)

# 別のスレッドでWebSocketサーバーを起動
thread = threading.Thread(target=server.run_forever)
thread.start()

print("start")
main()
