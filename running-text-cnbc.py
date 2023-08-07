# KODE MAIN RUNNING-TEXT GESER CNBC

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *
import json



cap = cv2.VideoCapture("../../cnbc-sejam/cnbc-sejam-duel2021.mp4")
#cap = cv2.VideoCapture("Videos/3mnt-cnbc.mp4")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# preprocess
height_process_top = round((23.5 / 27) * height)
height_process_bottom = round((26.5 / 27) * height) #26.5
width_process_left = round((1/7.6) * width)
width_process_right = round((6.2/7.6) * width)

iter = 0
frame_count = 0
sec = 0

flag_mulai = True

temp_result_atas = ""
temp_result_bawah = ""
temp_news = ["#&"]
temp_news_bawah = ["#&"]

time_atas = []
time_bawah = []

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
            element = len(result)
            # print(result)

            # biar iklan ga kebaca
            acc_lbound = 70 # bisa diatur sesuai frame maks video
            acc_rbound = 820 # bisa diatur juga

            if element==0:
                # atas
                if (temp_news[len(temp_news)-1] != "#&"):
                    if (temp_news[len(temp_news)-1][-1] != "&"):
                        temp_news[len(temp_news)-1] += "&"
                    temp_news.append("#&")

                # bawah
                if (temp_news_bawah[len(temp_news_bawah)-1] != "#&"):
                    if (temp_news_bawah[len(temp_news_bawah)-1][-1] != "&"):
                        temp_news_bawah[len(temp_news_bawah)-1] += "&"
                    temp_news_bawah.append("#&")


                print("\nTidak ada kalimat!")
            else:
                top_mostleft = result[0][0][0][0]
                top_mostright = result[-1][0][1][0]
                print("top left and top right:", top_mostleft," ",top_mostright)
                if top_mostleft<acc_lbound and top_mostright>acc_rbound:
                    result_diff = []
                    indeks = 0
                    # ini untuk pisah teks yang atas dan teks yang bawah
                    while indeks < len(result):
                        if result[indeks][0][2][1] > 60:
                            result_diff.append(result.pop(indeks))
                        else:
                            indeks += 1
                    
                    # ini untuk ketinggian
                    diff = 0
                    while diff < len(result_diff) :
                        if result_diff[diff][0][2][1] - result_diff[diff][0][1][1] < 30:
                            result_diff.pop(diff)
                        else:
                            diff += 1

                    

                    # ini untuk jarak antar boundbox
                    # if len(result_diff) != 0:
                    #     result_diff, arr_distance = distance_bbox(result_diff)
                    #     print("arr distance: ",arr_distance)
                    # print(result_diff)
                    frame_2 = bounding_box(result_diff,frame_2)
                    
                    

                    # main processing running text bagian atas
                    temp_result_atas = result[-2][1]
                    # if temp_news[-1][0].isdigit() and (not(temp_result_atas[0].isdigit())):
                    #     if temp_news[-1][-1]==")":
                    #         temp_news[-1] += "&"
                    if temp_news[-1][0].isdigit() and (not(temp_result_atas[0].isdigit())):
                        if temp_news[-1][0].isdigit() and temp_news[-1][-1]!="&": #dia kalo ngulang dapet digit lagi nanti malah duakali
                            temp_news[-1] += "&"
                    if sm(None, "".join(temp_news[-1]), "".join(temp_result_atas)).ratio() < 0.55:
                        temp_news.append(temp_result_atas)
                        if not(temp_news[-1][0].isdigit()):
                            time_atas.append(sec)

                    

                    # print("temp_news:",temp_news)
                    
                    # main processing running text bagian bawah
                    temp_result_bawah = result_diff[-2][1]
                    # print(temp_result_bawah,temp_news_bawah[-1])
                    if temp_news_bawah[-1][0].isdigit() and (not(temp_result_bawah[0].isdigit())):
                        if temp_news_bawah[-1][0].isdigit() and temp_news_bawah[-1][-1]!="&": #dia kalo ngulang dapet digit lagi nanti malah duakali
                            temp_news_bawah[-1] += "&"
                    if sm(None, "".join(temp_news_bawah[-1]), "".join(temp_result_bawah)).ratio() < 0.55:
                        temp_news_bawah.append(temp_result_bawah)
                        if not(temp_news_bawah[-1][0].isdigit()):
                            time_bawah.append(sec)

                    

                    # print("temp news bawah:",temp_news_bawah,"\n")

                    # print("time atas:",time_atas)
            

            # frame_count += 1
            # if frame_count>3600:
            # cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)
            sec+=1
            if sec>1000:
                break
            print("sec:",sec)
            print("----------------")
        iter += 1
    else:
        break

cap.release()
# cv2.destroyAllWindows()

# post processing
# atas
i=1
while True:
    if(temp_news[i][0].isalpha()) and (temp_news[i+1][0].isalpha()):
        temp_news[i] += "&"

    i+=1
    if i==len(temp_news)-1:
        break

# bawah
i=1
while True:
    if(temp_news_bawah[i][0].isalpha()) and (temp_news_bawah[i+1][0].isalpha()):
        temp_news_bawah[i] += "&"

    i+=1
    if i==len(temp_news_bawah)-1:
        break

# buat misahin per berita
# atas
news_out = []
news = "".join(temp_news)
news = news.split("&")
if len(news[-1])==0:
    news = news[:-1]
for i in range(len(news)):
    if not(news[i][0].isdigit()):
        if news[i]!="#":
            news_out.append(news[i])
print("news atas: ", news_out,"\n")
# bawah
news_bawah_out = []
news_bawah = "".join(temp_news_bawah)
news_bawah = news_bawah.split("&")
if len(news_bawah[-1])==0:
    news_bawah = news_bawah[:-1]
for i in range(len(news_bawah)):
    if not(news_bawah[i][0].isdigit()):
        if news_bawah[i]!="#":
            news_bawah_out.append(news_bawah[i])
print("news bawah: ",news_bawah_out,"\n")

for j in range(len(news_out)):
    print(news_out[j])

print("-------")

for k in range(len(news_bawah_out)):
    print(news_bawah_out[k])

print("-------")

# print(time_atas)
print(len(time_bawah))
print(len(news_bawah))
print(len(news_bawah_out))

print(len(time_atas))
print(len(news))
print(len(news_out))

# outputting .json
news_out_json = []
for i in range(len(news_out)):
    temp_json = [news_out[i],converttimestamp(time_atas[i])]
    news_out_json.append(temp_json)

cetak_json(news_out_json)