# KODE MAIN RUNNING-TEXT GESER

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *

cap = cv2.VideoCapture("Videos/simulasi-pasangan-capres-cawapres2.mp4")

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
                        if arr_distance[i] < 20:
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
                print("\nresult:")
                print(result)

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
                            news += temp_news[n:]
                            # aw = find_sentence(news, element)
                            # len_aw = len(aw)
                            # if len_aw > 0:
                            #     idx_dif = find_idx(yolo[len_yolo-1][0], aw)
                            #     if idx_dif < len_aw-1:
                            #         for idx in range(idx_dif+1, len_aw):
                            #             if len(aw[idx]) > 1:
                            #                 yolo[len_yolo][0] = aw[idx]
                            #                 yolo, len_yolo = add_element(
                            #                     yolo, len_yolo)
                            #                 yolo[idx_start][1] = time
                            #                 idx_start += 1
                            #     elif idx_dif == len_aw:
                            #         for idx in range(len_aw):
                            #             if len(aw[idx]) > 1:
                            #                 yolo[len_yolo][0] = aw[idx]
                            #                 yolo, len_yolo = add_element(
                            #                     yolo, len_yolo)
                            #                 yolo[idx_start][1] = time
                            #                 idx_start += 1
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

            # if f_bound:
                # if f_end:
                #     yolo[idx_end][2] = time
                #     idx_end += 1
                #     f_end = False
            # else:
            #     f_end = True

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

cap.release()
# cv2.destroyAllWindows()
yolo = similar(yolo, len_yolo)
cetak_json(yolo)
