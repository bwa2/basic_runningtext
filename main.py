import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

new_model = tf.keras.models.load_model('modelv1.h5')

for i in range(11):
    path = f"test_dir/{i}.png"
    img = image.load_img(path, target_size=(640,360))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    images = np.vstack([x])
    classes = new_model.predict(images, batch_size=10)
    print(classes)
    if classes[0][0] == 1:
        print("IKLAN")
    elif classes[0][1] == 1:
        print("INEWS")