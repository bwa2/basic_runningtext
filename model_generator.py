import tensorflow as tf
import splitfolders
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
import numpy as np

base_dir = 'dataset-tv'
new_dir = 'dataset-tv-devided'

splitfolders.ratio(base_dir, output="{}".format(new_dir),
                 seed=42, ratio=(.6, .4),
                group_prefix=None)

train_dir = f"{new_dir}/train"
val_dir = f"{new_dir}/val"


train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    fill_mode = 'nearest')

val_datagen = ImageDataGenerator(
                rescale=1. / 255)

train_gen = train_datagen.flow_from_directory(
                  train_dir,  # direktori data latih
                  target_size=(300, 300),  # 640x360 karena video resolusi 16:9
                  batch_size=32,      # batch akan mengambil 32 gambar sekli epoch
                  class_mode='categorical')

val_gen = val_datagen.flow_from_directory(
                  val_dir,  # direktori data validasi
                  target_size=(300, 300),  # 640x360 karena video resolusi 16:9
                  batch_size=32,    # semakin besar batch, semakin cepat program berjalan, namun semakin rendah akurasi
                  class_mode='categorical')

model = tf.keras.models.Sequential([
    # layer 1
    tf.keras.layers.Conv2D(32, (3,3), activation='relu',padding="same", input_shape=(300,300,3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    # layer 2
    tf.keras.layers.Conv2D(64, (3,3), activation='relu',padding="same"),
    tf.keras.layers.MaxPooling2D(2,2),
    # layer 3
    tf.keras.layers.Conv2D(128, (3,3), activation='relu',padding="same"),
    tf.keras.layers.MaxPooling2D(2,2),
    # layer 4
    tf.keras.layers.Conv2D(512, (3,3), activation='relu',padding="same"),
    tf.keras.layers.MaxPooling2D(2,2),
    # layer 6
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(512, activation='relu'),
    # output
    tf.keras.layers.Dense(2, activation='softmax')
])

model.compile(loss='categorical_crossentropy',
              optimizer=tf.keras.optimizers.legacy.Adam(),
              metrics=['accuracy'])

model.fit(
      train_gen,
      steps_per_epoch=20,  # berapa batch yang akan dieksekusi pada setiap epoch
      epochs=5, # tambahkan epochs jika akurasi model belum optimal
      validation_data=val_gen, # menampilkan akurasi pengujian data validasi
      validation_steps=5,  # berapa batch yang akan dieksekusi pada setiap epoch
      verbose=2)

model.save('modelv2.h5')





