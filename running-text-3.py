# KODE MAIN RUNNING-TEXT GESER

# UNSOLVEDCASE1: kalo ketika mulai ada tiga elemen
# UNSOLVEDCASE2: kalo kebanyakan mundur
# UNSOLVEDCASE3: kebaca sama ocr tiga elemen padahal harusnya dua elemen
#    sehingga berpengaruh ke perhitungan bound box starttime
# UNSOLVEDCASE4: elemennya kepisah dan tetep masuk news
# UNSOLVEDCASE5: berita baru mulai tetapi belum ada running-text

# SOLVED CASE:
# jika tiga kata pada news tdk sama dengan temp_news
# double ** karena sebelum break sudah ada asterisk
# boundnya pake count aja
# time saat break belum ada

import cv2
import easyocr
import torch
from difflib import SequenceMatcher as sm
from utils import *



cap = cv2.VideoCapture("../../INEWSSEJAM/inews-sejam-24juli.mp4")
#cap = cv2.VideoCapture("Videos/videosejam-720p2.mp4")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# preprocess
height_process_top = round((24.5 / 27) * height)
height_process_bottom = round((26 / 27) * height)
width_process_left = round((1.25999/7.6) * width)
width_process_right = round((7.6/7.6) * width)

iter = 0
frame_count = 0
sec = 0

flag_mulai = True

# timestamp
arr_start = [0]
arr_end = [0]
flag_timer = False
flag_timer_break = False # setelah break atau pertama kali
flag_timer_prebreak = False # flag timer buat break itu sendiri
flag_timer_prebreak_toggle = True
flag_barumulai = True
flag_check_iklan = False
sec2 = 0
counter = 0

news = ["#*"]

reader = easyocr.Reader(['id'], gpu=True)

while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:
            # preprocessing
            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_3 = frame
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            result = reader.readtext(frame_2,paragraph=True,x_ths=1.08,mag_ratio=1.4,blocklist='.')
            print(result)

            # main processing
            element = len(result) # kalimat berita
            temp_news = ""
            arr_distance, frame_2 = bounding_box(result,frame_2)
            print("arr distance: ",arr_distance)
            arr_bb_width = time_bbox(result)
            print("width of bound box: ",arr_bb_width)

            # biar iklan pendek ga kebaca


            acc_lbound = 100 # bisa diatur sesuai frame maks video
            acc_rbound = 1000 # bisa diatur juga

            # (news[len(news)-1]!="#START#*")
            if element==0:
                #nambah pager dan flag_mulai=true
                if (news[len(news)-1] != "#*"):
                    if (news[len(news)-1][-1] != "*"):
                        news[len(news)-1] += "*"

                    # if flag_check_iklan==True:
                    #     news.append("KEPOTONG*")
                    #     flag_check_iklan=False

                    news.append("#*")
                    flag_mulai = True
                print("\nTidak ada kalimat!")

                #masukin flag timer buat break
                if flag_timer_prebreak_toggle==True and flag_barumulai==False:
                    flag_timer_prebreak = True
                    print("---flag timer prebreak is true---")
            else:
                top_mostleft = result[0][0][0][0]
                top_mostright = result[-1][0][1][0]
                print("top left and top right:", top_mostleft," ",top_mostright)
                if top_mostleft<acc_lbound and top_mostright>acc_rbound:
                    if flag_mulai == True:
                        if element==2:
                            temp_news = result[1][1]

                            # flag_timer_prebreak_toggle=True
                    else:
                        temp_news = result[0][1]
                        if element > 1:
                            for i in range(1, element):
                                # disini taro if kalau bounding boxnya deket
                                # if distance antar bounding box tidak deket do the line below
                                # if arr_distance[i] < 25:
                                #     temp_news += " " + result[i][1]
                                #     if i == 1:
                                #         idx_bound = 1
                                # else:
                                #     temp_news += "* " + result[i][1]
                                temp_news += "* " + result[i][1]
                    temp_news = temp_news.split()
                    print("\ntemp_news:")
                    print(temp_news)

            len_temp = len(temp_news)
            if len_temp>5:
                temp_news = temp_news[:-1]

                if news[len(news)-1]=="#*":
                    news += temp_news
                    flag_mulai = False
                    flag_barumulai = False
                    print("---flag baru mulai is false---")
                    #starttime jalan pertama kali dan setelah break
                    flag_timer_prebreak_toggle = True
                    flag_timer_break = True
                    print("---flag timer break is true---")
                else:
                    idx_same = 0
                    for kata in temp_news:
                        if sm(None, "".join(news[-1]), "".join(kata)).ratio() >= 0.9:
                            idx_same+=1
                    n=idx_same
                    i=0
                    j=n
                    while(True):
                        # print(" ".join(news[-3:]))
                        # print(" ".join(temp_news))
                        if sm(None, "".join(news[-n:]), "".join(temp_news[i:j])).ratio() >= 0.91:
                            # perlu dicek apakah ada kata pada temp_news yang memiliki * sedangkan pada news tidak punya
                            temp_check = temp_news[i:j]
                            #temp_check2 = news[-3:]
                            #print(temp_check)
                            for i in range (len(temp_check)):
                                #print(kata)
                                if temp_check[i][-1]=="*":
                                    news=news[:-n]
                                    #print(news)
                                    news+=temp_check
                                    #print("THERE IS")
                            news += temp_news[j:]
                            #print("YES")
                            break
                        i += 1
                        j += 1
                        if j>len_temp:
                            news = news[:-1]
                            # if news[-1][-1]=="*":
                            #     flag_check_iklan = True
                            #     print("---FLAG CHECK ADA IKLAN IS TRUE---")
                            break

                    # normal timestamp extraction
                    # arr_bb_width, time, arr_start
                    # if len(arr_bb_width)>1:
                    #     if arr_bb_width[-1]<400 and arr_bb_width[-1]>100:
                    #         if counter>4:
                    #             flag_timer = True
                    #             print("---flag timer is true---")
                    # using asterisk instead:
                    temp_start = "".join(temp_news[-4:-1])
                    print("temp_start:",temp_start)
                    for huruf in temp_start:
                        if huruf=="*":
                            if counter>6:
                                flag_timer = True
                                print("---flag timer is true---")



                if (len(news)>20):
                    print("\nnews:")
                    news2=news
                    print(news2[-15:])

            sec += 1
            print("time:",sec)
            print("counter starttime:",counter)

            # if sec>3170:
            #     break

            if (flag_timer==True) or (flag_timer_break==True) or (flag_timer_prebreak==True):
                arr_start.append(sec)
                if flag_timer_break!=False:
                    flag_timer_break=False
                else:
                    flag_timer=False
                    if flag_timer_prebreak!=False:
                        flag_timer_prebreak_toggle=False
                        print("---flag timer pre break toggle is false---")
                    flag_timer_prebreak=False
                    counter = 0




            counter += 1

            print("starttime: ",arr_start)
            print("\n--------\n")
            # show video
            # cv2.imshow("frame", frame_2)
            # key = cv2.waitKey(10)

            # frame_count += 1
            # if frame_count>3600:
            # cv2.imwrite(f'frame_{frame_count}.jpg', frame_3)


        iter += 1
    else:
        break




cap.release()
# cv2.destroyAllWindows()

# post processing
last_time = sec
temp_arr_end = arr_start[2:]
arr_end += temp_arr_end
for i in range(len(arr_end)):
    if i!=0:
        arr_end[i] += 9
arr_end.append(last_time)

#ubah ke format time stamp
# for i in range (len(arr_start)):
#     arr_start[i] = converttimestamp(arr_start[i])

# for i in range (len(arr_end)):
#     arr_end[i] = converttimestamp(arr_end[i])

print("news:",news)
print("arr start:",arr_start)
print("arr end:",arr_end)


# buat misahin per berita
panjang_news = len(news)
arr_text = ['']
jml_berita = 0
ada_titik = False
for i in range(panjang_news):
    temp_word = news[i]
    for j in range(len(temp_word)):
        if temp_word[j] == '*':
            ada_titik = True
            temp_word = temp_word[0:i]
        else:
            ada_titik = False
    if arr_text == ['']:
        arr_text[jml_berita] += temp_word
    else:
        arr_text[jml_berita] += " " + temp_word

    if ada_titik:
        print("jml berita: ", jml_berita)
        jml_berita += 1
        arr_text.append('')
jml_berita += 1

# cek repitisi
arr_repetition = []
for i in range(len(arr_text)):
    arr_repetition.append(0)
    for j in range(len(arr_text)):
        if i != j:
            if arr_text[i] == arr_text[j]:
                arr_repetition[i] += 1

    #print(arr_repetition)

for i in range(len(arr_text)):
    print("\ntext:",arr_text[i])

for i in range(len(arr_start)):
    print("\ntimestamp:",converttimestamp(arr_start[i]))

print("\nrepeat: ",arr_repetition)

# print("\nberita:",arr_text)
print("\njumlah berita:", jml_berita, "len berita:", len(arr_text), "len arr start:",len(arr_start),"len arr end:",len(arr_end))


# masukin ke json
input_json = [{}]

for i in range(jml_berita):
    temp_json = {"text": arr_text[i],"start time": converttimestamp(arr_start[i]), "end time": converttimestamp(arr_end[i]), "duration": arr_end[i] - arr_start[i],"repeat": arr_repetition[i] }
    input_json[i] = temp_json
    #print(input_json)
    if(i != jml_berita-1):
        input_json.append({})

with open("1.json", "w") as f:
    json.dump(input_json,f, indent=3)
f.close()