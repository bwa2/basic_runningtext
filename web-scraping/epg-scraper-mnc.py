from bs4 import BeautifulSoup
import requests
import time
import json
from datetime import datetime

# inisiasi waktu
ts = time.time()
today = datetime.now()
d1 = today.strftime("%Y-%m-%d")

# inisiasi pengambilan data dari web rctiplus
url = 'https://www.rctiplus.com/tv/mnctv/'
page = requests.get(url)
page_html = page.text

# menyimpan data html dalam file
with open('today.html', 'w') as f:
        f.write(page_html)


# mengolah informasi dari file html
with open('today.html') as fp:
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
       'channel': "MNCTV",
       'fetched': ts,
       'source': 'rctiplus.com',
       'programme': []
}

for e in arr_info:
      new_json['programme'].append({
             'start': d1 + "T" + e[1][0] + ":00+07:00",
             'stop': d1 + "T" + e[1][1]+ ":00+07:00",
             'title': e[0]
        })

with open("Today.json", 'w') as fp:
        json.dump(new_json, fp, indent=3)
