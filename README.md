### KODE RUNNING TEXT

UNTUK MENDETEKSI RUNNING TEXT PADA BERITA DENGAN TIPE GESER

kode main: running-text.py

### Link PPT Progress Report
https://docs.google.com/presentation/d/1uT46h8e-D52uhlJnKPk6wt-T0V81LEN-wrc3GRWHvTY/edit?usp=sharing

### Link Log Book
https://docs.google.com/document/d/1ZuIEfDKig_7JhB5wOIf6MBJ3fEMlySfAGmN0LGrgE2E/edit

### Run docker container
```
docker kill etoe-livetv
docker run --rm -d --gpus all \
--shm-size=12g \
--name=nolimit_image2text_engine \
--network host \
-v $HOME:$HOME \
-v /nfs:/nfs \
-w /home/ubuntu/workspace/intern/test/basic_runningtext \
risetai/image2text:latest tail -f /dev/null
```

### Attach to container bash
```
docker exec -it nolimit_image2text_engine bash
```
