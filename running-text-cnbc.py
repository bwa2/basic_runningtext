# KODE MAIN RUNNING-TEXT GESER CNBC

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *



#cap = cv2.VideoCapture("../../INEWSSEJAM/inews-sejam-24juli.mp4")
cap = cv2.VideoCapture("Videos/3mnt-cnbc.mp4")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# preprocess
height_process_top = round((23.5 / 27) * height)
height_process_bottom = round((25 / 27) * height) #26.5
width_process_left = round((1/7.6) * width)
width_process_right = round((6.2/7.6) * width)

iter = 0
frame_count = 0
sec = 0

flag_mulai = True


temp_result = ""
temp_news = ["#&"]

reader = easyocr.Reader(['id'], gpu=True)

while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:
            # preprocessing
            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # preprocessing tambahan
            # frame_2 = cv2.GaussianBlur(frame_2,(5,5),0)
            # #img = cv2.medianBlur(img, 3)
            # a, frame_2 = cv2.threshold(frame_2, 120, 255, cv2.THRESH_BINARY)
            # frame_2 = cv2.fastNlMeansDenoisingColored(frame_2, None, 10, 10, 7, 15)    

            # ocr
            result = reader.readtext(frame_2,mag_ratio=1.3)
            print(result)
            
            temp_result = result[-2][1]
            
            if sm(None, "".join(temp_news[-1]), "".join(temp_result)).ratio() < 0.85:
                temp_news.append(temp_result)

            if temp_news[-1][-1]==")":
                temp_news[-1] += "&"


            print("temp_news:",temp_news)
            arr_distance, frame_2 = bounding_box(result,frame_2)
            print("arr distance: ",arr_distance)
            print("----------------")


            frame_count += 1
            # if frame_count>3600:
            cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)
            sec+=1
            if sec>15:
                break
        iter += 1
    else:
        break

cap.release()
# cv2.destroyAllWindows()

# buat misahin per berita
news = " ".join(temp_news)
news = news.split("&")
if len(news[-1])==0:
    news = news[:-1]
print(news)