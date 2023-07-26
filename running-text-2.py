# KODE MAIN RUNNING-TEXT GESER

# UNSOLVEDCASE1: kalo ketika mulai ada tiga elemen
# UNSOLVEDCASE2: kalo kebanyakan mundur

# SOLVED CASE: 
# jika tiga kata pada news tdk sama dengan temp_news
# double ** karena sebelum break sudah ada asterisk
# 

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *

cap = cv2.VideoCapture("Videos/videosejam-720p2.mp4")

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
                if (news[len(news)-1] != "#*"):
                    if (news[len(news)-1][-1] != "*"):
                        news[len(news)-1] += "*"
                    news.append("#*")
                    flag_mulai = True
                print("\nTidak ada kalimat!")
            else:
                if flag_mulai == True:
                    if element==2:
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
                else:
                    i=0
                    j=3
                    while(True):
                        # print(" ".join(news[-3:]))
                        # print(" ".join(temp_news))
                        if sm(None, " ".join(news[-3:]), " ".join(temp_news[i:j])).ratio() >= 0.915:
                            news += temp_news[j:]
                            break
                        i += 1
                        j += 1
                        if j>len_temp:
                            news = news[:-3]
                            break
                    
                
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
            # if sec>800:
            #     break
        iter += 1
    else:
        break



cap.release()
# cv2.destroyAllWindows()

# buat misahin per berita
panjang_news = len(news)
arr_text = ['']
jml_berita = 0
ada_titik = False
for i in range(panjang_news):
    temp_word = news[i]
    for j in range(len(temp_word)):
        if temp_word[j] == '*':
            ada_titik = True
            temp_word = temp_word[0:i]
        else:
            ada_titik = False
    if arr_text == ['']:
        arr_text[jml_berita] += temp_word
    else:
        arr_text[jml_berita] += " " + temp_word
        
    if ada_titik:
        print("jml berita: ", jml_berita)
        jml_berita += 1
        arr_text.append('')
jml_berita += 1

print("\nberita:",arr_text)
print("\njumlah berita:", jml_berita, "len berita:", len(arr_text))
