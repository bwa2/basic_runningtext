import cv2
import tensorflow as tf
import os
import numpy as np
from tensorflow.keras.preprocessing import image

detik =0
frame_count = 0
iter = 0
detik_iklan = []
frame_3 = []

logdir = './frames'
if not os.path.exists(logdir):
    os.makedirs(logdir)


cap = cv2.VideoCapture('cek-iklan2-inews.mp4')

# video properti
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))

model = tf.keras.models.load_model('modelv2.h5')

while cap.isOpened():
    ret,frame = cap.read()
    if ret:
        if (iter%fps) == 0:
            detik += 1 
            
            frame_2 = cv2.resize(frame, (300, 300))
            x = np.expand_dims(frame_2,0)

            if detik == 3:
                frame_3 = x
            

            classes = model.predict(x)
            print(classes)

            print("detik: ", detik)
            if classes[0][0] == 1:
                print("IKLAN")
                detik_iklan.append(detik)
            elif classes[0][1] == 1:
                print("INEWS")
            
            frame_count += 1
            cv2.imwrite(f'./frames/frame_{frame_count}.jpg', frame_2)
        iter += 1
    else:
        break

print(detik_iklan)

#f = open("liat2.txt", "a")

#f.write(f"{frame_3}")
#f.close()

cap.release()