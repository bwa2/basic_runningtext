# KODE MAIN RUNNING-TEXT GESER

# UNSOLVEDCASE1: kalo ketika mulai ada tiga elemen

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *

cap = cv2.VideoCapture("Videos/cek-iklan2-inews.mp4")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# preprocess
height_process_top = round((24.5 / 27) * height)
height_process_bottom = round((26 / 27) * height)
width_process_left = round((1.25999/7.6) * width)
width_process_right = round((7.6/7.6) * width)

iter = 0
frame_count = 0
sec = 0

flag_mulai = True

news = ["#*"]

reader = easyocr.Reader(['id'], gpu=True)

while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:
            # preprocessing
            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            result = reader.readtext(frame_2)

            # main processing
            element = len(result) # kalimat berita
            temp_news = ""
            arr_distance = bounding_box(result)
            print("arr distance: ",arr_distance)

            
            if element==0:
                #nambah pager dan flag_mulaitrue

                print("\nTidak ada kalimat!")
            else:
                if flag_mulai == True:
                    temp_news = result[1][1]
                else:
                    temp_news = result[0][1]
                    if element > 1:
                        for i in range(1, element):
                            # disini taro if kalau bounding boxnya deket
                            # if distance antar bounding box tidak deket do the line below
                            if arr_distance[i] < 25:
                                temp_news += " " + result[i][1]
                                if i == 1:
                                    idx_bound = 1
                            else:
                                temp_news += "* " + result[i][1]
                temp_news = temp_news.split()
                print("\ntemp_news:")
                print(temp_news)

            len_temp = len(temp_news)
            if len_temp>5:
                temp_news = temp_news[:-1]

                if news[len(news)-1]=="#*":
                    news += temp_news
                    flag_mulai = False
                    print("a")
                else:
                    i=0
                    j=3
                    while(True):
                        # print(" ".join(news[-3:]))
                        # print(" ".join(temp_news))
                        if sm(None, " ".join(news[-3:]), " ".join(temp_news[i:j])).ratio() >= 0.915:
                            print("c")
                            break
                        i += 1
                        j += 1
                    print("b")
                
                print("\nnews:")
                print(news)



            # show video
            '''cv2.imshow("frame", frame_2)
            key = cv2.waitKey(10)

            frame_count += 1
            cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)'''
            sec += 1
            print("time:",sec)
            print("\n--------\n")
            if sec>800:
                break
        iter += 1
    else:
        break



cap.release()
# cv2.destroyAllWindows()

