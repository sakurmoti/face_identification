import cv2
import os
import numpy as np
import json
import base64

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def show_image():
    for file in get_file_path('./dataset'):
        data = json.load(open(file))
        print("name: {}".format(data['name']))

        for image in data['images']:
            # base64でエンコードされた画像をデコード
            print(len(image))
            prefix = 'data:image/png;base64,'
            image = image[len(prefix):]
            decoded = base64.b64decode(image)
            img = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
            print(type(img))
            print(img.shape)
            # cv2.imshow('image', img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

def get_file_path(folder_path):
    files = os.listdir(folder_path)
    files_file = [('{}/{}'.format(folder_path,f)) for f in files if os.path.isfile(os.path.join(folder_path, f))]
    return files_file

def update_database(name, id):
    fr = open('database.json', 'r', encoding='utf-8')
    data = json.load(fr)
    fr.close()

    if(str(id) not in data.keys()):
        data.update({id: name})

    fw = open('database.json', 'w', encoding='utf-8')
    json.dump(data, fw, indent=4)
    fw.close()

def make_EigenFaceTrainer():
    recognizer = cv2.face.EigenFaceRecognizer_create()
    faces, ids = [], []
    max_size = -1
    for file in get_file_path('./dataset'):
        data = json.load(open(file))
        print("name: {}".format(data['name']))
        id = data['id']

        for image in data['images']:
            prefix = 'data:image/png;base64,'
            image = image[len(prefix):]
            decoded = base64.b64decode(image)
            img = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face = face_cascade.detectMultiScale(gray, 1.3, 5)

            try:
                if(face.shape[0] > 1):
                    print("顔が複数検出されました。")
                    continue
            except:
                print("顔が検出されませんでした。")
                continue

            for (x,y,w,h) in face:
                max_size = max(max_size, h, w)
                face_img = gray[y:y+h, x:x+w]
                faces.append(face_img)
                ids.append(id)

        if(len(faces) > 0):
            recognizer.train(faces, np.array(ids))
            recognizer.save('trainer.yml')
            update_database(data['name'], id)
        else:
            print("顔が1つも検出されませんでした。")
    

def make_LBPHtrainer():
    # https://docs.opencv.org/2.4/modules/contrib/doc/facerec/facerec_tutorial.html
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = [], []
    for file in get_file_path('./dataset'):
        data = json.load(open(file))
        print("name: {}".format(data['name']))
        id = data['id']

        for image in data['images']:
            # base64でエンコードされた画像をデコード
            prefix = 'data:image/png;base64,'
            image = image[len(prefix):]
            decoded = base64.b64decode(image)
            img = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face = face_cascade.detectMultiScale(gray, 1.3, 5)

            # 顔は一人で撮ることを想定
            try:
                if(face.shape[0] > 1):
                    print("顔が複数検出されました。")
                    continue
            except:
                print("顔が検出されませんでした。")
                # cv2.imshow('image', img)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                continue

            
            # 顔を切り抜き
            for (x,y,w,h) in face:
                face_img = gray[y:y+h, x:x+w]
                faces.append(face_img)
                ids.append(id)

    # https://docs.opencv.org/4.x/dd/d65/classcv_1_1face_1_1FaceRecognizer.html#ac8680c2aa9649ad3f55e27761165c0d6
    if(len(faces) > 0):
        recognizer.train(faces, np.array(ids))
        recognizer.save('trainer.yml')

        # 顔の名前を更新
        update_database(data['name'], id)
    else:
        print("顔が1つも検出されませんでした。")


print(get_file_path('./dataset'))
# show_image()
make_LBPHtrainer()