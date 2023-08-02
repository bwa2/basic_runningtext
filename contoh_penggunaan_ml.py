# CARA PENGGUNAAN
# Download terlebih dahulu model di https://drive.google.com/file/d/1wapNSst2IlPui8HIki7PWYkfGWW7Nmc5/view?usp=sharing
# jangan lupa install tensorflow, numpy, dan
# pip install pyyaml h5py  (untuk mengakses model .h5)

import cv2
import tensorflow as tf
import os
import numpy as np
from tensorflow.keras.preprocessing import image

detik =0
frame_count = 0
iter = 0

cap = cv2.VideoCapture('cek-iklan2-inews.mp4')

# mengimport file model yang ada di gdrive 
model = tf.keras.models.load_model('modelv2.h5')

while cap.isOpened():
    ret,frame = cap.read()
    if ret:
        if (iter%fps) == 0:
            detik += 1 

            # menginput frame video ke dalam format yang dapat diterima
            frame_2 = cv2.resize(frame, (300, 300))
            x = np.expand_dims(frame_2,0)

            # model melakukan prediksi dari frame yang telah diformat
            classes = model.predict(x)
            print(classes)

            # mengekstrak hasil prediksi
            if classes[0][0] == 1:
                print("IKLAN")
                detik_iklan.append(detik)
            elif classes[0][1] == 1:
                print("INEWS")
                
        iter += 1
    else:
        break

cap.release()
