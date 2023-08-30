from bs4 import BeautifulSoup
import requests
import time
import json
from datetime import datetime
import argparse
import os

# inisiasi waktu
ts = time.time()
today = datetime.now()
d1 = today.strftime("%Y-%m-%d")


def main():
        # args
        a = argparse.ArgumentParser(description='Update recording schedule to crontab')
        ch = "MNCTV"
        #print(ch)
        #print("test")
        if (ch == "MNCTV") or (ch == "MNC TV"):
                ch = "MNC"


        if ch == "MNC" or ch == "INEWS":
                # inisiasi pengambilan data dari web rctiplus
                url_mnc = 'https://www.rctiplus.com/tv/mnctv/'
                url_inews = 'https://www.rctiplus.com/tv/inews'

                if ch == 'MNC':
                        url = url_mnc
                elif ch == 'INEWS':
                        url = url_inews

                page = requests.get(url)
                page_html = page.text

                # menyimpan data html dalam file
                with open(f'{ch}_html_{d1}.html', 'w') as f:
                        f.write(page_html)


                # mengolah informasi dari file html
                with open(f'{ch}_html_{d1}.html') as fp:
                        main_soup = BeautifulSoup(fp, "html.parser")

                infos = main_soup.find_all("div", class_="now-playing")
                arr_info = [] #['Judul', ['Jam_mulai', 'Jam_selesai']]
                i = 0

                for info in infos:
                        isi = info.text
                        arr_info.append(isi.strip("\n").split("\n"))
                        arr_info[i][1] = arr_info[i][1].split(" - ") 
                        #print(arr_info[i][1])
                        i += 1


                # menginput informasi ke JSON
                new_json = {
                        'channel': ch,
                        'fetched': ts,
                        'source': 'rctiplus.com',
                        'programme': []
                }


                for e in arr_info:
                        stop_now = (int(e[1][1][0:2])*60 + int(e[1][1][3:5]))
                        start_now = (int(e[1][0][0:2])*60 + int(e[1][0][3:5]))
                        duration = stop_now -  start_now # akhirb - awalb

                        if duration >= 0:
                                new_json['programme'].append({
                                                'start': d1 + "T" + e[1][0] + ":00+07:00",
                                                'stop': d1 + "T" + e[1][1]+ ":00+07:00",
                                                'duration': duration,
                                                'title': e[0]
                                        })
                        else:
                                new_json['programme'].append({
                                                'start': d1 + "T" + e[1][0] + ":00+07:00",
                                                'stop': d1 + "T" + e[1][1]+ ":00+07:00",
                                                'duration': ((int(e[1][1][0:2]) + 24)*60 + int(e[1][1][3:5])) - (int(e[1][0][0:2])*60 + int(e[1][0][3:5])),
                                                'title': e[0]
                                        })

                # membuat folder jika belum ada
                logdir = f'./epg/{ch}'
                if not os.path.exists(logdir):
                        os.makedirs(logdir)

                # json untuk hari ini
                with open(f'epg/{ch}/Today.json', 'w') as fp:
                        json.dump(new_json, fp, indent=3)
                
                # json untuk archive
                with open(f'epg/{ch}/{today.strftime("%Y-%m-%dT%H:%M:%S")}.json', "w") as fp:
                        json.dump(new_json, fp, indent=3)
        else:
                print("This program's for MNC or INEWS only")

if __name__ == '__main__':
    main()
