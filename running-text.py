# KODE MAIN RUNNING-TEXT GESER

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *
import argparse
from datetime import datetime
import config
# import tensorflow as tf
import os
import os.path
import numpy as np
# from tensorflow.keras.preprocessing import image

def inews_mnc (cap, fps, height_process_top, height_process_bottom,  width_process_left, width_process_right) :
    iter = 0
    sec = 0
    flag_mulai = True

    # timestamp
    arr_start = [0]
    arr_end = [0]
    flag_timer = False
    flag_timer_break = False # setelah break atau pertama kali
    flag_timer_prebreak = False # flag timer buat break itu sendiri
    flag_timer_prebreak_toggle = True
    flag_barumulai = True
    flag_check_iklan = False
    flag_iklan = False
    sec2 = 0
    counter = 0

    news = ["#*"]

    reader = easyocr.Reader(['id'], gpu=True)

    # mengimport file model yang ada di gdrive https://drive.google.com/file/d/1wapNSst2IlPui8HIki7PWYkfGWW7Nmc5/view?usp=sharing
    # model = tf.keras.models.load_model('../../modelv2.h5')

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:

            if (iter % ((fps))) == 0:
                # preprocessing
                frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #frame_3 = frame
                frame_2 = frame_2[height_process_top:height_process_bottom,
                                width_process_left:width_process_right]
                
                # menginput frame video ke dalam format yang dapat diterima
                frame_ml = cv2.resize(frame, (300, 300))
                x = np.expand_dims(frame_ml,0)

                # model melakukan prediksi dari frame yang telah diformat
                # classes = model.predict(x)
                # print(classes)

                # ocr
                result = reader.readtext(frame_2,paragraph=True,x_ths=1.08,mag_ratio=1.4,blocklist='.')
                print(result)

                # main processing
                element = len(result) # kalimat berita
                temp_news = ""
                arr_distance, frame_2 = bounding_box(result,frame_2)
                print("arr distance: ",arr_distance)
                arr_bb_width = time_bbox(result)
                print("width of bound box: ",arr_bb_width)

                # biar iklan ga kebaca
                acc_lbound = 100 # bisa diatur sesuai frame maks video
                acc_rbound = 1000 # bisa diatur juga
                # mengekstrak hasil prediksi
                # if classes[0][0] == 1:
                #     print("IKLAN")
                #     flag_iklan = True
                # elif classes[0][1] == 1:
                #     print("INEWS")
                #     flag_iklan = False

                # (news[len(news)-1]!="#START#*")
                if element==0:
                    #nambah pager dan flag_mulai=true
                    if (news[len(news)-1] != "#*"):
                        if (news[len(news)-1][-1] != "*"):
                            news[len(news)-1] += "*"

                        # if flag_check_iklan==True:
                        #     news.append("KEPOTONG*")
                        #     flag_check_iklan=False

                        news.append("#*")
                        flag_mulai = True
                    print("\nTidak ada kalimat!")

                    #masukin flag timer buat break
                    if flag_timer_prebreak_toggle==True and flag_barumulai==False:
                        flag_timer_prebreak = True
                        print("---flag timer prebreak is true---")
                else:
                    top_mostleft = result[0][0][0][0]
                    top_mostright = result[-1][0][1][0]
                    print("top left and top right:", top_mostleft," ",top_mostright)
                    if top_mostleft<acc_lbound and top_mostright>acc_rbound:
                    # if flag_iklan==False:
                        if flag_mulai == True:
                            if element==2:
                                temp_news = result[1][1]

                                # flag_timer_prebreak_toggle=True
                        else:
                            temp_news = result[0][1]
                            if element > 1:
                                for i in range(1, element):
                                    # disini taro if kalau bounding boxnya deket
                                    # if distance antar bounding box tidak deket do the line below
                                    if arr_distance[i] < 35:
                                        temp_news += " " + result[i][1]
                                        if i == 1:
                                            idx_bound = 1
                                    else:
                                        temp_news += "* " + result[i][1]
                                    #temp_news += "* " + result[i][1]
                        temp_news = temp_news.split()
                        print("\ntemp_news:")
                        print(temp_news)

                len_temp = len(temp_news)
                if len_temp>5:
                    temp_news = temp_news[:-1]

                    if news[len(news)-1]=="#*":
                        news += temp_news
                        flag_mulai = False
                        flag_barumulai = False
                        print("---flag baru mulai is false---")
                        #starttime jalan pertama kali dan setelah break
                        flag_timer_prebreak_toggle = True
                        flag_timer_break = True
                        print("---flag timer break is true---")
                    else:
                        idx_same = 1
                        count_same=0
                        while True:
                            #print(news[-idx_same:])
                            for z in range(len(temp_news)):
                                if sm(None, "".join(news[-idx_same:]), "".join(temp_news[z:z+idx_same])).ratio() >= 0.92:
                                    #print("YES")
                                    count_same+=1
                                    
                            if count_same>1:
                                idx_same+=1
                                #print(idx_same)
                                count_same=0
                            else:
                                break
                        n=idx_same
                        i=0
                        j=n
                        print("news ke -n:",news[-n:])
                        
                        while(True):
                            # print(" ".join(news[-3:]))
                            # print(" ".join(temp_news))
                            if sm(None, "".join(news[-n:]), "".join(temp_news[i:j])).ratio() >= 0.91:
                                temp_check = temp_news[i:j]
                                #temp_check2 = news[-3:]
                                #print(temp_check)
                                for k in range (len(temp_check)):
                                    #print(kata)
                                    if temp_check[k][-1]=="*":
                                        news=news[:-n]
                                        #print(news)
                                        news+=temp_check
                                        #print("THERE IS")
                                news += temp_news[j:]
                                #print("YES")
                                break
                            i += 1
                            j += 1
                            if j>len_temp:
                                print("YESSS")
                                news = news[:-1]
                                # if news[-1][-1]=="*":
                                #     flag_check_iklan = True
                                #     print("---FLAG CHECK ADA IKLAN IS TRUE---")
                                break

                        # normal timestamp extraction
                        # arr_bb_width, time, arr_start
                        # if len(arr_bb_width)>1:
                        #     if arr_bb_width[-1]<400 and arr_bb_width[-1]>100:
                        #         if counter>4:
                        #             flag_timer = True
                        #             print("---flag timer is true---")
                        # using asterisk instead:
                        temp_start = "".join(temp_news[-4:-1])
                        print("temp_start:",temp_start)
                        for huruf in temp_start:
                            if huruf=="*":
                                if counter>6:
                                    flag_timer = True
                                    print("---flag timer is true---")



                    if (len(news)>20):
                        print("\nnews:")
                        news2=news
                        print(news2[-15:])

                sec += 1
                print("time:",sec)
                print("counter starttime:",counter)

                # if sec>3170:
                #     break

                if (flag_timer==True) or (flag_timer_break==True) or (flag_timer_prebreak==True):
                    arr_start.append(sec)
                    if flag_timer_break!=False:
                        flag_timer_break=False
                    else:
                        flag_timer=False
                        if flag_timer_prebreak!=False:
                            flag_timer_prebreak_toggle=False
                            print("---flag timer pre break toggle is false---")
                        flag_timer_prebreak=False
                        counter = 0

                counter += 1

                print("starttime: ",arr_start)
                print("\n--------\n")
                # show video
                # cv2.imshow("frame", frame_2)
                # key = cv2.waitKey(10)

                # frame_count += 1
                # if frame_count>3600:
                # cv2.imwrite(f'frame_{frame_count}.jpg', frame_3)


            iter += 1
        else:
            break

    cap.release()
    # cv2.destroyAllWindows()

    # post processing
    last_time = sec
    temp_arr_end = arr_start[2:]
    arr_end += temp_arr_end
    for i in range(len(arr_end)):
        if i!=0:
            arr_end[i] += 9
    arr_end.append(last_time)

    print("news:",news)
    print("arr start:",arr_start)
    print("arr end:",arr_end)

    # OUTPUTTING
    # buat misahin per berita
    arr_text = []
    news = " ".join(news)
    arr_text = news.split("*")
    if len(arr_text[-1])==0:
        arr_text = arr_text[:-1]

    # cek repitisi
    arr_repetition = []
    for i in range(len(arr_text)):
        arr_repetition.append(0)
        for j in range(len(arr_text)):
            if i != j:
                if arr_text[i] == arr_text[j]:
                    arr_repetition[i] += 1

        #print(arr_repetition)

    for i in range(len(arr_text)):
        print("\ntext:",arr_text[i])

    for i in range(len(arr_start)):
        print("\ntimestamp:",converttimestamp(arr_start[i]))

    print("\nrepeat: ",arr_repetition)

    # print("\nberita:",arr_text)
    print("\njumlah berita:", len(arr_text), "len berita:", len(arr_text), "len arr start:",len(arr_start),"len arr end:",len(arr_end))

    # masukin ke json
    input_json = [{}]

    for i in range(len(arr_text)):
        temp_json = {"text": arr_text[i],"start time": converttimestamp(arr_start[i]), "end time": converttimestamp(arr_end[i]), "duration": arr_end[i] - arr_start[i],"repeat": arr_repetition[i] }
        input_json[i] = temp_json
        #print(input_json)
        if(i != len(arr_text)-1):
            input_json.append({})
    
    name = args.channel
    name = name.upper()
    nama_folder(name, input_json)

def cnbc (cap, fps, height_process_top, height_process_bottom,  width_process_left, width_process_right) :
    iter = 0
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
                print(result)

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
                        
                        # filter untuk ketinggian text box
                        # atas
                        diff = 0
                        while diff < len(result) :
                            if result[diff][0][2][1] - result[diff][0][1][1] < 30:
                                result.pop(diff)
                            else:
                                diff += 1
                        # bawah
                        diff = 0
                        while diff < len(result_diff) :
                            if result_diff[diff][0][2][1] - result_diff[diff][0][1][1] < 30:
                                result_diff.pop(diff)
                            else:
                                diff += 1

                        # print(result)
                        # print(result_diff)

                        # ini untuk jarak antar boundbox
                        if len(result) != 0 and len(result_diff)!=0:
                            result, arr_distance = distance_bbox(result)
                            print("arr distance: ",arr_distance)

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

                            

                            print("temp_news:",temp_news)
                            
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

                            

                            print("temp news bawah:",temp_news_bawah,"\n")

                            # print("time atas:",time_atas)
                

                # frame_count += 1
                # if frame_count>3600:
                # cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)
                sec+=1
                # if sec>3000:
                    # break
                print("sec:",sec)
                print("----------------")
            iter += 1
        else:
            break

    cap.release()
    # cv2.destroyAllWindows()

    # post processing
    # atas
    for i in range(len(temp_news) - 1):
        if (temp_news[i][0].isalpha()) and (temp_news[i+1][0].isalpha()):
            temp_news[i] += "&"

    # bawah
    for i in range(len(temp_news_bawah) - 1):
        if(temp_news_bawah[i][0].isalpha()) and (temp_news_bawah[i+1][0].isalpha()):
            temp_news_bawah[i] += "&"

    # buat misahin per berita
    # atas
    news_out = []
    news = ""
    for i in range(len(temp_news)):
        news += temp_news[i] + " "
    news = news.split("& ")
    if len(news[-1])==0:
        news = news[:-1]
    for i in range(len(news)):
        if not(news[i][0].isdigit()):
            if news[i]!="#":
                news_out.append(news[i])
    print("news atas: ", news_out,"\n")
    # bawah
    news_bawah_out = []
    news_bawah = ""
    for i in range(len(temp_news_bawah)):
        news_bawah += temp_news_bawah[i] + " "
    news_bawah = news_bawah.split("& ")
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

    name = args.channel
    name = name.upper()
    nama_folder(name, news_out_json)

# Running channel
running = {
    "inews": inews_mnc,
    "mnc": inews_mnc,
    "cnbc": cnbc
}

mapping_config = {
    "inews": config.inews,
    "mnc": config.mnc,
    "cnbc": config.cnbc
}

# preprocess
a = argparse.ArgumentParser(description='input data')
a.add_argument("-c", "--channel", required=True, help="channel's name. Example: --c MNC")
a.add_argument("-v", "--video", required=True, help="Video path. Example: -v Videos/vidio-inews-long.mp4")
args = a.parse_args()

path = args.video

# check whether video is available
check_file = os.path.exists(path)
while check_file!=True:
    check_file = os.path.exists(path)

if check_file:
    cap = cv2.VideoCapture(f"{path}")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frame_1 = args.channel
frame_1 = frame_1.lower()

selected_func = mapping_config[frame_1]

height_process_top, height_process_bottom,  width_process_left, width_process_right = selected_func(width, height)

if frame_1 in running:
    running[frame_1](cap, fps, height_process_top, height_process_bottom,  width_process_left, width_process_right)
else:
    print("Nama channel tidak valid.")
