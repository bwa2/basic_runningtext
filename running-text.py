# sudah ada safety buat kalau ada jeda running-text dan ada salah baca easyocr
# TODOTOM : count_mismatch tidak ke reset kalau tidak masuk ke kondisi if (DONE)
# TODOAGAIN : check berapa persen yang sama antara tiap kalimat berita supaya bisa tau munculnya berapa kali
# karena ada beberapa yang terputus akibat gagal identifikasi oleh ocr
# TODOTWO : KALAU LAGI BREAK, langsung lanjut gausah ngecek ke belakang lagi (batasnya 15 detik)


import cv2
import easyocr
import torch
import json


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
    elm.append([0, 0, 0, 0])
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


cap = cv2.VideoCapture("video-inews-long.mp4")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

iter = 0
frame_count = 0
news = ["#*"]
yolo = [["#*", 0, 0, 0], [0, 0, 0, 0]]
len_yolo = 1
last_sentence = ""
time = 0

idx_start = 1
idx_end = 1

while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:

            # preprocess
            height_process_top = round((24.5 / 27) * height)
            height_process_bottom = round((26 / 27) * height)
            width_process_left = round((1.25999/7.6) * width)
            width_process_right = round((7.6/7.6) * width)

            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            reader = easyocr.Reader(['id'], gpu=True)
            result = reader.readtext(frame_2)

            #
            element = len(result)
            temp_news = ""

            if element == 0:
                if (news[len(news)-1] != "#*"):
                    news[len(news)-1] += "*"
                    yolo, len_yolo = add_element(yolo, len_yolo)
                    yo = find_sentence(news, 2)
                    yolo[len_yolo-1][0] = yo

                    for i in range(idx_end, len_yolo):
                        yolo[i][2] = time
                        idx_end += 1
                    news.append("#*")
                    yolo, len_yolo = add_element(yolo, len_yolo)
                    yo = find_sentence(news, 2)
                    yolo[len_yolo-1][0] = yo
                print("\nTidak ada kalimat!")
            else:
                temp_news = result[0][1]
                if element > 1:
                    for i in range(1, element):
                        temp_news += "* " + result[i][1]
                temp_news = temp_news.split()
                print("\ntemp_news:")
                print(temp_news)

            len_temp = len(temp_news)
            if (len_temp != 0):
                # mengambil kalimat sampai kata kedua dari akhir
                temp_news = temp_news[:-1]

                if news[len(news)-1] == "#*":
                    news += temp_news
                    yolo[idx_start][1] = time
                    idx_start += 1
                else:
                    i = 0
                    f_same = False
                    while (i < len_temp and f_same == False):
                        if news[-2:] == temp_news[0:2]:
                            news += temp_news[2:]
                            aw = find_sentence(news, element)
                            if len(aw) > 0:
                                for idx in range(element):
                                    if yolo[len_yolo-1][0] != aw[idx-1]:
                                        yolo[len_yolo][0] = aw[idx-1]
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
                print("\nyolo:")
                print(yolo)

            # show video
            # cv2.imshow("frame", frame_2)
            # key = cv2.waitKey(10)

            # frame_count += 1
            # cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)
            time += 1
        iter += 1
    else:
        break

cap.release()
# cv2.destroyAllWindows()
