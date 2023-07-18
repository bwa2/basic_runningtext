# sudah ada safety buat kalau ada jeda running-text dan ada salah baca easyocr
# TODOTOM : count_mismatch tidak ke reset kalau tidak masuk ke kondisi if (DONE)
# TODOAGAIN : check berapa persen yang sama antara tiap kalimat berita supaya bisa tau munculnya berapa kali 
# karena ada beberapa yang terputus akibat gagal identifikasi oleh ocr
# TODOTWO : KALAU LAGI BREAK, langsung lanjut gausah ngecek ke belakang lagi (batasnya 15 detik)


import cv2
import easyocr
import torch
import json
import difflib

cap = cv2.VideoCapture("inews-2-720.mp4")

# get video property
fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

iter = 0
frame_count = 0
news = []
compare = []

# safety ketika running text hilang
flag_mismatch = 0
count_mismatch = 0
break_counter = 0
max_break = 15

while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        if (iter % ((fps))) == 0:

            # preprocess
            height_process_top = round((24.5 / 27) * height)
            height_process_bottom = round((26 / 27) * height)
            width_process_left = round((1.25999/7.6) * width)
            width_process_right = round((7.6/7.6) * width)

            frame_2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_2 = frame_2[height_process_top:height_process_bottom,
                              width_process_left:width_process_right]

            # ocr
            reader = easyocr.Reader(['id'], gpu=True)
            result = reader.readtext(frame_2)

            #
            element = len(result)
            temp_news = ""

            if element == 0:
                print("\nTidak ada kalimat!")
                break_counter += 1
                print("\nbreak counter:")
                print(break_counter)
            else:
                if flag_mismatch==1:
                    if(element>1):
                        temp_news = result[1][1]
                        temp_news = temp_news.split()
                        print("\ntemp_news saat mismatch:")
                        print(temp_news)
                    else:
                        temp_news = ""
                        print("\nNEXT NEWS NOT FOUND YET!!!")
                else:                    
                    temp_news = result[0][1]
                    if element > 1:
                        for i in range(1, element):
                            temp_news += "* " + result[i][1]
                    temp_news = temp_news.split()
                    print("\ntemp_news:")
                    print(temp_news)

            len_temp = len(temp_news)
            if  (len_temp!=0):
                temp_news = temp_news[:-1] #mengambil kalimat sampai kata kedua dari akhir
                
                if len(news) == 0 or (flag_mismatch==1) or (max_break<break_counter):
                    if flag_mismatch!=0:
                        flag_mismatch=0
                    
                    if(break_counter!=0):
                        break_counter=0
                        print("\nbreak counter:")
                        print(break_counter)

                    news += temp_news
                else:
                    compare = news[-2:]
                    while(True):
                        i=0
                        if compare[0:1]==temp_news[0:1]:
                            if compare[1:2]==temp_news[1:2]:
                                count_mismatch=0
                                news+=temp_news[2:]
                                break
                            else:
                                if i==len(temp_news):
                                    if (max_break>break_counter):
                                        print("MISMATCH OCCURED, REVERTING ONE TIME")
                                        news=news[:-1]
                                        count_mismatch+=1
                                        break
                                    else:
                                        break
                                temp_news = temp_news[1:]
                        else:
                            if i==len(temp_news):
                                if (max_break>break_counter):
                                    print("MISMATCH OCCURED, REVERTING ONE TIME")
                                    news=news[:-1]
                                    count_mismatch+=1
                                    break
                                else:
                                    break
                            temp_news = temp_news[1:]
                        i+=1
                    if (count_mismatch>2):
                        # tambahin asterisk di kata news[-1]
                        news[-1]+= "*"
                        # dilanjutkan dengan memulai ulang lagi dari ketika membaca ada dua element
                        # realisasi dengan flag
                        count_mismatch = 0
                        flag_mismatch = 1

                        print("\nMISMATCH BETWEEN NEWS AND TEMP_NEWS")

                print("\nnews:")
                print(news)

                print("\n count mismatch:")
                print(count_mismatch)

            #show video
            cv2.imshow("frame", frame_2)
            key = cv2.waitKey(10)

            # frame_count += 1
            # cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)

        iter += 1
    else:
        break

cap.release()
#cv2.destroyAllWindows()


#merging berita
panjang_news = len(news)
arr_text = ['']
jml_berita = 0
ada_titik = False

for i in range(panjang_news):
    temp_word = news[i]
    for i in range(len(temp_word)):
        if temp_word[i] == '*':
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
# arr_repetition = []
# for i in range(len(arr_text)):
#     arr_repetition.append(0)
#     for j in range(len(arr_text)):
#         if i != j:
#             if arr_text[i] == arr_text[j]:
#                 arr_repetition[i] += 1
    
    #print(arr_repetition)



# cek similarity
arr_repetition = []
arr_similar = []
for i in range (len(arr_text)) :
    arr_repetition.append(0)
    for j in range (len(arr_text)) :
        if i!=j :
            if arr_text[i] == arr_text[j]:
                    arr_repetition[i] += 1
            
            else : 
                string1 = arr_text[i]
                string2 = arr_text[j]
                
                temp = difflib.SequenceMatcher(None,string1 ,string2)

                if temp.ratio() > 0.9 :
                    if len(arr_text[i]) > len(arr_text[j]) :
                        print(f"kalimat 1 : {arr_text[i]}")
                        print(f"kalimat 2 : {arr_text[j]}")
                        print('Similarity Score: ',temp.ratio())
                        arr_text[j] = arr_text[i]
                        arr_repetition[i] += 1
                        arr_similar[i] += temp.ratio()
                    
                    elif len(arr_text[i]) < len(arr_text[j]) :
                        print(f"kalimat 1 : {arr_text[i]}")
                        print(f"kalimat 2 : {arr_text[j]}")
                        print('Similarity Score: ',temp.ratio())
                        arr_text[i] = arr_text[j]
                        arr_repetition[j] += 1
                        arr_similar[i] += temp.ratio
                    
                    else : 
                        print(f"kalimat 1 : {arr_text[i]}")
                        print(f"kalimat 2 : {arr_text[j]}")
                        print('Similarity Score: ',temp.ratio())
                        arr_similar[i] += temp.ratio()
                

print("text:\n",arr_text)
print("repeat: ",arr_repetition)

# masukin ke json
input_json = [{}]

for i in range(jml_berita):
    temp_json = {"text": arr_text[i],"time": None,"repeat": arr_repetition[i], "similarity":  arr_similar[i]}
    input_json[i] = temp_json
    print(input_json)
    if(i != jml_berita-1):
        input_json.append({})

with open("hasilnyacobafinal_5_ke1.json", "w") as f:
    json.dump(input_json,f, indent=3)
f.close()

print(arr_text)