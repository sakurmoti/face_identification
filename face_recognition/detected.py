import cv2
import time
from websocket_server import WebsocketServer
import threading
import signal
import sys
import argparse


class FaceDetector:
    def __init__(self, cascade_path):
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.detected_printed = False
        self.last_detected_time = None

    def detect_faces(self, gray, minW, minH):
        return self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

    def process_frame(self, img, cam, server):
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.detect_faces(gray, minW, minH)

        if len(faces) > 0:
            if not self.detected_printed:
                message = '{"isDetected" : true}'
                server.send_message_to_all(message)
                print("検出")
                self.detected_printed = True
            self.last_detected_time = time.time()
        elif self.last_detected_time and time.time() - self.last_detected_time > 5 and self.detected_printed:
            message = '{"isDetected" : false}'
            server.send_message_to_all(message)
            print("非検出")
            self.detected_printed = False

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)


def signal_handler(sig, frame, server):
    print("Shutting down gracefully...")
    server.shutdown()
    cv2.destroyAllWindows()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Face Detector with optional window display")
    parser.add_argument('-w', '--window', default="off", choices=["on", "off"], help="Display camera window (default: off)")
    args = parser.parse_args()  # コマンドライン引数を解析

    face_detector = FaceDetector('haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    server = WebsocketServer(host="127.0.0.1", port=5001)
    server.set_fn_new_client(lambda client, server: print("New client connected"))
    server.set_fn_client_left(lambda client, server: print("Client disconnected"))
    server.set_fn_message_received(lambda client, server, message: None)

    thread = threading.Thread(target=server.run_forever)
    thread.start()

    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, server))

    print("start")
    while True:
        ret, img = cam.read()
        face_detector.process_frame(img, cam, server)
        time.sleep(0.1)
        if args.window == "on":  # オプションでカメラウィンドウを表示する条件を追加
            cv2.imshow('camera', img)
        if cv2.waitKey(10) & 0xff == 27:
            break

    print("プログラムを終了します。")
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
