# # Membuat array pertama
# array_sumber = [([[16, 0], [278, 0], [278, 32], [16, 32]], 'BARITO PACIFIC 770', 0.9587160214037711), 
#                 ([[308, 2], [433, 2], [433, 33], [308, 35]], '25 (3,33%)', 0.4345254166182505), 
#                 ([[450, 0], [807, 0], [807, 32], [450, 36]], 'BUMI SERPONG DAMAI 1125', 0.8148056629915795)]

# #Membuat array kedua untuk menyimpan nilai lebih dari 5
# array_tujuan = []

# # Loop untuk memindahkan nilai lebih dari 5 dan menghapusnya dari array pertama
# indeks = 0
# while indeks < len(array_sumber):
#     if array_sumber[indeks][0][2][1] > 32:
#         array_tujuan.append(array_sumber.pop(indeks))
#     else:
#         indeks += 1

# # Cetak hasilnya
# print("Array sumber setelah dipindahkan:", array_sumber)
# print("Array tujuan:", array_tujuan[0])

import cv2
import easyocr
import torch
import json
import numpy as np




cap = cv2.VideoCapture('Videos/vidio-inews-tv.mkv')

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

iter = 0
frame_count = 0
news = []
while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % (7*fps)) == 0:

            # preprocess
            height_process_top = round((24.5 / 27) * height)
            height_process_bottom = round((26 / 27) * height)
            width_process_left = round((1.25999/7.6) * width)
            width_process_right = round((7.6/7.6) * width)

            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            reader = easyocr.Reader(['id'], gpu=False)
            result = reader.readtext(frame_2)


            #
            element = len(result)
            temp_news = ""

            if element == 0:
                print("Tidak ada kalimat!")
            else:
                temp_news = result[0][1]
                if element > 1:
                    for i in range(1, element):
                        box1 = result[0][1]
                        box2 = result[1][1]

                        temp_news += "* " + result[i][1]
                     

                temp_news = temp_news.split()
                print("\ntemp_news:")
                print(temp_news)

            temp_news = temp_news[:-1]
            len_temp = len(temp_news)
            if len(news) == 0:
                news = temp_news
            else:
                i = 1
                while (i):
                    if news[-1:] == temp_news[0:1]:
                        news += temp_news[1:]
                        i = 0
                    else:
                        temp_news = temp_news[1:]
                        i=1
                    
            print("\nnews:")
            print(news)

            count = 0
            arr_tx = []
            arr_bx = []
            arr_bx_arr = []
            arr_tx_arr = []
            # show video
            for (coord, text, prob) in result:
                (topleft, topright, bottomright, bottofleft) = coord
                tx, ty = (int(topleft[0]), int(topleft[1]))
                bx, by = (int(bottomright[0]), int(bottomright[1]))
                cv2.rectangle(frame_2, (tx, ty), (bx, by), (0, 0, 255), 2)
                count += 1
                arr_bx.append(bx)
                arr_tx.append(tx)

                for i in range (count-1) :
                    arr_bx_arr.append(arr_bx[i])
                    arr_tx_arr.append(arr_tx [i+1])
            
            print (arr_bx_arr, arr_tx_arr)

            if (len(arr_tx_arr)) == 1 :
                distance = arr_tx_arr[0] - arr_bx_arr[0]
                print(f"jarak drawing bound : {distance}")
            elif (len(arr_tx_arr)) > 1 :
                for j in range (len(arr_tx_arr)) :
                    if j != 0 :
                        distance = arr_tx_arr[j] - arr_bx_arr[j]
                        print(f"jarak drawing bound ke -{j} : {distance}")


        

            frame_count += 1
            cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)

        iter += 1
    else:
        break

cap.release()
cv2.destroyAllWindows()