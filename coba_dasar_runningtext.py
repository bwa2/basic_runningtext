import cv2
import sys
import os
import easyocr
import pandas as pd
import torch

iter = 0
detik = 0

# ngambil video
cap = cv2.VideoCapture('Videos/0-0-21.mp4')

# video properti
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

# loop mengambil frame
while cap.isOpened():
    ret, frame = cap.read()
    # conditional "ret" digunakan untuk mengecek apakah cap.read() masih berjalan. Jika cap.read() masih berjalan, maka ret bernilai True
    if ret:
        # conditional "iter" digunakan agar proses textreading tidak dilakukan setiap loop, akan tetapi hanya saat (iter % fps) == 0
        if (iter % fps) == 0:
            detik += 1
            print("detik: ", detik)

            # preprocess
            width_process = round((1/7.6) * width)
            height_process = round((20 / 27) * height)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = frame_rgb[height_process:height, width_process:width]

            # menampilkan video preprocess
            cv2.imshow("frame_rgb", frame_rgb)
            key = cv2.waitKey(30)
            if key == 10:
                break

            # melakukan textdetection
            reader = easyocr.Reader(['id'], gpu=True)
            result = reader.readtext(frame_rgb)
            len_result = len(result)
            if len_result > 1:
                for i in range(len_result):
                    print("RESULT KE-"+ str(i) + ':')
                    print(" ", result[i][1])
            else:
                print("RESULT: \n", result[0][1])
            print("")
        iter += 1
    else:
        break

cap.release()

