# sudah ada safety buat kalau ada jeda running-text dan ada salah baca easyocr
# TODOTOM : count_mismatch tidak ke reset kalau tidak masuk ke kondisi if (DONE)
# TODOAGAIN : check berapa persen yang sama antara tiap kalimat berita supaya bisa tau munculnya berapa kali
# karena ada beberapa yang terputus akibat gagal identifikasi oleh ocr
# TODOTWO : KALAU LAGI BREAK, langsung lanjut gausah ngecek ke belakang lagi (batasnya 15 detik)


import cv2
import easyocr
import torch
import json
from difflib import SequenceMatcher as sm
import argparse
import time
import datetime
import os

a = argparse.ArgumentParser(description='input data')
a.add_argument("-c", "--channel", required=True, help="channel's name. Example: --c MNC")
a.add_argument("-v", "--video", required=True, help="Video path. Example: -v Videos/vidio-inews-long.mp4")
args = a.parse_args()

def find_idx(news, temp_news):
    len_temp_news = len(temp_news)
    idx = 0
    f_match = True
    while idx < len_temp_news and f_match:
        if news == temp_news[idx]:
            f_match = False
            return idx
        idx += 1

    print(idx)
    return idx


def find_sentence(temp_news, n_sentence):
    f_asterisk = 0
    n_temp_news = len(temp_news)
    idx_temp_news = n_temp_news - 1
    sentence = []

    i = 0
    while (f_asterisk < n_sentence and idx_temp_news > -1):
        if temp_news[idx_temp_news][len(temp_news[idx_temp_news])-1] == "*":
            f_asterisk += 1

        if f_asterisk > 0 and f_asterisk < n_sentence:
            sentence.insert(0, temp_news[idx_temp_news])
        idx_temp_news -= 1

    yolo = ["" for i in range(n_sentence-1)]
    idx_yolo = 0
    for i in range(len(sentence)):
        yolo[idx_yolo] += sentence[i] + " "

        if sentence[i][len(sentence[i])-1] == "*":
            yolo[idx_yolo] = yolo[idx_yolo][:-2]
            idx_yolo += 1

    return yolo


def add_element(elm, n_elm):
    elm.append(["", 0, 0, 0])
    n_elm += 1
    return elm, n_elm


def last_temp(temp):
    n_temp = len(temp)
    result = []
    found = False
    while (n_temp > 0 and found == False):
        if temp[n_temp-1][len(temp[n_temp-1])-1] == "*":
            found = True
        else:
            result.insert(0, temp[n_temp-1])
        n_temp -= 1
    return result


def bounding_box(result):
    # cek bounding box
    count_2 = 0
    arr_tx = []
    arr_bx = []
    arr_bx_arr = []
    arr_tx_arr = []
    arr_distance = [0]
    # show video
    for (coord, text, prob) in result:
        (topleft, topright, bottomright, bottofleft) = coord
        tx, ty = (int(topleft[0]), int(topleft[1]))
        bx, by = (int(bottomright[0]), int(bottomright[1]))
        cv2.rectangle(frame_2, (tx, ty), (bx, by), (0, 0, 255), 2)
        count_2 += 1
        arr_bx.append(bx)
        arr_tx.append(tx)

        for i in range(count_2-1):
            arr_bx_arr.append(arr_bx[i])
            arr_tx_arr.append(arr_tx[i+1])

    if (len(arr_tx_arr)) == 1:
        distance = arr_tx_arr[0] - arr_bx_arr[0]
        # print("jarak drawing bound : ",distance)
        arr_distance.append(distance)
    elif (len(arr_tx_arr)) > 1:
        for j in range(len(arr_tx_arr)):
            if j != 0:
                distance = arr_tx_arr[j] - arr_bx_arr[j]
                # print(f"jarak drawing bound ke -{j} : {distance}")
                arr_distance.append(distance)
    return arr_distance


def find_asterisk(str):
    asterisk = False
    n_str = len(str)
    i = 0

    while i < n_str and asterisk == False:
        if str[i] == "*":
            asterisk = True

        i += 1
    return asterisk


def find_same(str_1, str_2):
    n = 2
    len_str_2 = len(str_2)
    match = True
    while n < 4 and match:
        i = 0
        while i < len_str_2-n:
            if str_1[-n:] == str_2[i:i+n]:
                n += 1
            i += 1

        if i == len_str_2-n:
            match = False

    return n


def cetak_json(news):
    input_json = []
    j = 0
    jml_berita = len(news)

    for i in range(jml_berita):
        if ((news[i][0] != "#*") and (news[i][0] != "*") and (news[i][0] != "#")) and (len(news[i][0]) > 1):
            temp_json = {"text": news[i][0], "start time": news[i][1], "end time": news[i]
                         [2], "duration": news[i][2] - news[i][1], "repeat": news[i][3]}
            input_json.append({})
            input_json[j] = temp_json
            j += 1

    timestamp = time.time()

    waktu = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')

    name = args.channel
    name = name.upper()
    filename = name + "-" + waktu + ".json"

    if not os.path.exists(filename) :
        with open(filename,'w', newline='') as f :
            with open("cobatime2.json", "w") as f:
                json.dump(input_json, f, indent=3)
            f.close()
    else :
        with open(filename,'a', newline='') as f :
            with open("cobatime2.json", "w") as f:
                json.dump(input_json, f, indent=3)
            f.close()
    
    print("idx j")
    print(j)
    print("jml berita")
    print(jml_berita)


def similar(arr, pjg):
    arr_repetition = []
    arr_text = []
    for i in range(pjg):
        arr_text.append(arr[i][0])

    for i in range(len(arr_text)):
        arr_repetition.append(0)
        for j in range(len(arr_text)):
            if i != j:
                if arr_text[i] == arr_text[j]:
                    arr_text[i] = arr_text[i].upper()
                    arr_text[j] = arr_text[j].upper()
                    arr_repetition[i] += 1

                else:
                    string1 = arr_text[i]
                    string2 = arr_text[j]

                    temp = sm(None, string1, string2)

                    if temp.ratio() > 0.9:
                        if len(arr_text[i]) > len(arr_text[j]):
                            print(f"kalimat 1 : {arr_text[i]}")
                            print(f"kalimat 2 : {arr_text[j]}")
                            print('Similarity Score: ', temp.ratio())
                            arr_text[j] = arr_text[i]
                            arr_text[i] = arr_text[i].upper()
                            arr_text[j] = arr_text[j].upper()
                            arr_repetition[i] += 1

                        elif len(arr_text[i]) < len(arr_text[j]):
                            print(f"kalimat 1 : {arr_text[i]}")
                            print(f"kalimat 2 : {arr_text[j]}")
                            print('Similarity Score: ', temp.ratio())
                            arr_text[i] = arr_text[j]
                            arr_text[i] = arr_text[i].upper()
                            arr_text[j] = arr_text[j].upper()
                            arr_repetition[i] += 1

                        else:
                            print(f"kalimat 1 : {arr_text[i]}")
                            print(f"kalimat 2 : {arr_text[j]}")
                            print('Similarity Score: ', temp.ratio())
                            arr_text[i] = arr_text[i].upper()
                            arr_text[j] = arr_text[j].upper()

        for i in range(pjg):
            arr[i][0] = arr_text[i]

    return arr

path = args.video

cap = cv2.VideoCapture(f"{path}")

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
news = ["#*"]
yolo = [["#*", 0, 0, 0], ["", 0, 0, 0]]
len_yolo = 1
last_sentence = ""
time = 0

idx_start = 1
idx_end = 1
f_bound = False
f_end = True
bound = 0
idx_bound = 0

reader = easyocr.Reader(['id'], gpu=True)
while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:
            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            result = reader.readtext(frame_2)

            #
            element = len(result)
            temp_news = ""
            arr_distance = bounding_box(result)

            if element == 0:
                if (news[len(news)-1] != "#*"):
                    news[len(news)-1] += "*"
                    yolo, len_yolo = add_element(yolo, len_yolo)
                    yo = find_sentence(news, 2)
                    yolo[len_yolo-1][0] = yo[0]

                    for i in range(idx_end, len_yolo):
                        yolo[i][2] = time
                        idx_end += 1
                    news.append("#*")
                    yolo, len_yolo = add_element(yolo, len_yolo)
                    yo = find_sentence(news, 2)
                    yolo[len_yolo-1][0] = yo[0]
                    idx_start += 1

                f_bound = False
                print("\nTidak ada kalimat!")
            else:
                temp_news = result[0][1]
                if element > 1:
                    for i in range(1, element):
                        # disini taro if kalau bounding boxnya deket
                        # if distance antar bounding box tidak deket do the line below
                        if arr_distance[i] < 30:
                            temp_news += " " + result[i][1]
                            if i == 1:
                                idx_bound = 1
                        else:
                            temp_news += "* " + result[i][1]
                temp_news = temp_news.split()
                f_asterisk = find_asterisk("".join(temp_news[:2]))
                bound = result[idx_bound][0][1][0]
                if bound < 200:
                    f_bound = True
                else:
                    f_bound = False
                idx_bound = 0

                print("\ntemp_news:")
                print(temp_news)
                # print("\nresult:")
                # print(result)

            len_temp = len(temp_news)
            if (len_temp > 1):
                # mengambil kalimat sampai kata kedua dari akhir
                temp_news = temp_news[:-1]

                if news[len(news)-1] == "#*":
                    news += temp_news
                    yolo[idx_start][1] = time
                    idx_start += 1
                else:
                    i = 0
                    f_same = False
                    n = find_same(news, temp_news)
                    while (i < len_temp and f_same == False):
                        if sm(None, " ".join(news[-n:]), " ".join(temp_news[0:n])).ratio() >= 0.915:
                            if ''.join(temp_news[0:n]).count('*'):
                                news[-n:] = temp_news[0:n]
                            news += temp_news[n:]
                            aw = find_sentence(news, element)
                            len_aw = len(aw)
                            if len_aw > 0:
                                idx_dif = find_idx(yolo[len_yolo-1][0], aw)
                                if idx_dif < len_aw-1:
                                    for idx in range(idx_dif+1, len_aw):
                                        if len(aw[idx]) > 1:
                                            yolo[len_yolo][0] = aw[idx]
                                            yolo, len_yolo = add_element(
                                                yolo, len_yolo)
                                            yolo[idx_start][1] = time
                                            idx_start += 1
                                elif idx_dif == len_aw:
                                    for idx in range(len_aw):
                                        if len(aw[idx]) > 1:
                                            yolo[len_yolo][0] = aw[idx]
                                            yolo, len_yolo = add_element(
                                                yolo, len_yolo)
                                            yolo[idx_start][1] = time
                                            idx_start += 1
                            f_same = True
                        else:
                            temp_news = temp_news[1:]

                        i += 1
                    if f_same == False and i == len_temp:
                        news = news[:-1]

                print("\nnews:")
                print(news)
                # print("\nyolo:")
                # print(yolo)

            if f_bound:
                if f_end:
                    yolo[idx_end][2] = time
                    idx_end += 1
                    f_end = False
            else:
                f_end = True

            # show video
            '''cv2.imshow("frame", frame_2)
            key = cv2.waitKey(10)

            frame_count += 1
            cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)'''
            time += 1
            print("time:",time)
            if time>800:
                break
        iter += 1
    else:
        break

yolo[len_yolo][0] = "#*"

for i in range(idx_end, len_yolo):
    yolo[i][2] = time
    idx_end += 1

print("\nyolo:")
print(yolo)

cap.release()
# cv2.destroyAllWindows()
# yolo = similar(yolo, len_yolo)
# cetak_json(yolo)
