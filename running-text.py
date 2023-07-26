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

def add_element(elm, n_elm):
    elm.append(["", 0, 0, 0])
    n_elm += 1
    return elm, n_elm


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


def find_same(str_1, str_2):
    n = 2
    len_str_2 = len(str_2)
    match = True
    while n < 4 and match:
        i = 0
        while i < len_str_2-n:
            if sm(None, ' '.join(str_1[-n:]), ' '.join(str_2[i:i+n])).ratio() >= 0.915:
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


cap = cv2.VideoCapture("simulasi-pasangan-capres-cawapres-cut.mp4")

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

news = [["#*", 0, 0, 0], ["", 0, 0, 0]]
temp_news = ["#*"]
time = 0

idx_start = 1
f_start = False
f_insert_start = True

idx_end = 1
f_end = False
f_insert_end = True

idx_bound_start = 0
idx_bound_end = 0

reader = easyocr.Reader(['id'], gpu=True)
while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:
            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            result_ocr = reader.readtext(frame_2)
            n_result = len(result_ocr)
            temp_result = ""
            arr_distance = bounding_box(result_ocr)
            f_initial = False

            if n_result == 0:
                if (temp_news[len(temp_news)-1] != '#*'):
                    if temp_news[len(temp_news)-1][len(temp_news[len(temp_news)-1])-1] != '*':
                        temp_news[len(temp_news)-1] += '*'
                    temp_news.append('#*')

                    for i in range(idx_end, idx_start):
                        news[i][2] = time
                        news, idx_start = add_element(news, idx_start)
                        
                f_end = False
                print("\nTidak ada kalimat!")
            else:
                temp_result = result_ocr[0][1]
                idx_bound_start = n_result - 1
                idx_bound_end = 0
                if n_result > 1:
                    for i in range(1, n_result):
                        # disini taro if kalau bounding boxnya deket
                        # if distance antar bounding box tidak deket do the line below
                        if arr_distance[i] < 30:
                            temp_result += " " + result_ocr[i][1]
                            if i == 1:
                                idx_bound_end = i
                        else:
                            temp_result += "* " + result_ocr[i][1]
                            idx_bound_start = i

                if idx_bound_start != -1:
                    bound_start = result_ocr[idx_bound_start][0][0][0]
                    if bound_start < width_process_right - 360:
                        f_start = True
                    else:
                        f_start = False

                bound_end = result_ocr[idx_bound_end][0][1][0]
                if bound_end < 200:
                    f_end = True
                else:
                    f_end = False

                print("\ntemp_result:")
                print(temp_result)
                print(f'\nbound_start : bound = {bound_start} : {width_process_right - 360}')

            temp_result = temp_result.split()
            n_temp_result = len(temp_result)
            if (n_temp_result > 1):
                # mengambil kalimat sampai kata kedua dari akhir
                temp_result = temp_result[:-1]

                if temp_news[len(temp_news)-1] == "#*":
                    temp_news += temp_result
                    for i in range(n_result):
                        news[idx_start][1] = time
                        news, idx_start = add_element(news, idx_start)
                    f_initial = True
                    f_insert_start = False
                else:
                    i = 0
                    f_same = False
                    n = find_same(temp_news, temp_result)
                    while (i < n_temp_result and f_same == False):
                        temp_result_join = ' '.join(temp_result[:n])
                        if sm(None, ' '.join(temp_news[-n:]), temp_result_join).ratio() >= 0.915:
                            if temp_result_join.count('*') != 0:
                                temp_news[-n:] = temp_result[:n]
                            temp_news += temp_result[n:]
                            f_same = True
                        else:
                            temp_result = temp_result[1:]
                        i += 1

                    if f_same == False and i == n_temp_result:
                        temp_news = temp_news[:-1]

            if f_start:
                if f_insert_start and f_initial == False:
                    news[idx_start][1] = time
                    news, idx_start = add_element(news, idx_start)
                    f_insert_start = False
            else:
                f_insert_start = True

            if f_end:
                if f_insert_end:
                    news[idx_end][2] = time
                    idx_end += 1
                    f_insert_end = False
            else:
                f_insert_end = True

            # show video
            '''cv2.imshow("frame", frame_2)
            key = cv2.waitKey(10)

            frame_count += 1
            cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)'''
            time += 1
            print("time:",time)
        iter += 1
    else:
        break

for i in range(idx_end, idx_start):
    news[i][2] = time

temp_news = ' '.join(temp_news).split('* ')
for i in range(idx_start):
    news[i][0] = temp_news[i]

print(f'\nnews:\n{news}')
print(f'\ntemp_news:\n{" ".join(temp_news)}')
print(f'\nlen_news:\n{len(news)}')
print(f'len_temp_news:\n{" ".join(temp_news).count("*")}')

cap.release()
cv2.destroyAllWindows()
news = similar(news, idx_start)
cetak_json(news)
