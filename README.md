KODE RUNNING TEXT

UNTUK MENDETEKSI RUNNING TEXT PADA BERITA DENGAN TIPE GESER

kode main: running-text.py

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
docker exec -it nolimit_image2text_engine bash
