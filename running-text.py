# sudah ada safety buat kalau ada jeda running-text dan ada salah baca easyocr
# TODOTOM : count_mismatch tidak ke reset kalau tidak masuk ke kondisi if (DONE)
# TODOAGAIN : check berapa persen yang sama antara tiap kalimat berita supaya bisa tau munculnya berapa kali
# karena ada beberapa yang terputus akibat gagal identifikasi oleh ocr
# TODOTWO : KALAU LAGI BREAK, langsung lanjut gausah ngecek ke belakang lagi (batasnya 15 detik)


import cv2
import easyocr
import torch
import json


def find_idx(news, temp_news):
    len_temp_news = len(temp_news)
    idx = 0
    f_match = True
    while idx < len_temp_news and f_match:
        if news == temp_news[idx]:
            print("BENARRRR")
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
    arr_distance= [0]
    # show video
    for (coord, text, prob) in result:
        (topleft, topright, bottomright, bottofleft) = coord
        tx, ty = (int(topleft[0]), int(topleft[1]))
        bx, by = (int(bottomright[0]), int(bottomright[1]))
        #cv2.rectangle(frame_2, (tx, ty), (bx, by), (0, 0, 255), 2)
        count_2 += 1
        arr_bx.append(bx)
        arr_tx.append(tx)

        for i in range (count_2-1) :
            arr_bx_arr.append(arr_bx[i])
            arr_tx_arr.append(arr_tx [i+1])

    if (len(arr_tx_arr)) == 1 :
        distance = arr_tx_arr[0] - arr_bx_arr[0]
        #print("jarak drawing bound : ",distance)
        arr_distance.append(distance)
    elif (len(arr_tx_arr)) > 1 :
        for j in range (len(arr_tx_arr)) :
            if j != 0 :
                distance = arr_tx_arr[j] - arr_bx_arr[j]
                #print(f"jarak drawing bound ke -{j} : {distance}")
                arr_distance.append(distance)
    return arr_distance

def cetak_json(news):
    input_json = []
    j = 0
    jml_berita = len(news)

    for i in range(jml_berita):
        if ((news[i][0] != "#*") and (news[i][0] != "*") and (news[i][0] != "#")) and (len(news[i][0]) > 1):
            temp_json = {"text": news[i][0],"start time": news[i][1], "end time": news[i][2], "duration": news[i][1] - news[i][2],"repeat": news[i][3] }
            input_json.append({})
            input_json[j] = temp_json
            j += 1
        
    with open("cobatime2.json", "w") as f:
        json.dump(input_json,f, indent=3)
    f.close()

cap = cv2.VideoCapture("Videos/vidio-inews-tv.mkv")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

iter = 0
frame_count = 0
news = ["#*"]
yolo = [["#*", 0, 0, 0], ["", 0, 0, 0]]
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
                print("\nTidak ada kalimat!")
            else:
                temp_news = result[0][1]
                if element > 1:
                    for i in range(1, element):
                        #disini taro if kalau bounding boxnya deket
                        #if distance antar bounding box tidak deket do the line below
                        if arr_distance[i]<25:
                            temp_news += " " + result[i][1]
                        else:
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
                            len_aw = len(aw)
                            if len_aw > 0:
                                idx_dif = find_idx(yolo[len_yolo-1][0], aw)
                                if idx_dif < len_aw-1:
                                    for idx in range(idx_dif+1, len_aw):
                                        yolo[len_yolo][0] = aw[idx]
                                        yolo, len_yolo = add_element(
                                            yolo, len_yolo)
                                        yolo[idx_start][1] = time
                                        idx_start += 1
                                elif idx_dif == len_aw:
                                    for idx in range(len_aw):
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
cetak_json(yolo)
