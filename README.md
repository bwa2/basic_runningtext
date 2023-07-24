KODE RUNNING TEXT

UNTUK MENDETEKSI RUNNING TEXT PADA BERITA DENGAN TIPE GESER

kode buat inews: running-text-inews.py

github pc token:
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

git remote set-url origin https://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@github.com/bwa2/basic_runningtext

### Run docker container
```
docker kill etoe-livetv
docker run --rm -d --gpus all \
--shm-size=12g \
--name=nolimit_image2text_engine \
--network host \
-v $HOME:$HOME \
-v /nfs:/nfs \
-w /home/ubuntu/workspace/intern \
risetai/image2text:latest tail -f /dev/null
```

### Attach to container bash
docker exec -it nolimit_image2text_engine bash
