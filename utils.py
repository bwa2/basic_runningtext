import cv2
import json
from difflib import SequenceMatcher as sm
from datetime import timedelta


def distance_bbox(result):
    n = len(result)
    distance = 0
    temp= []
    arr = []
    i=0
    while True:
        distance = result[i+1][0][3][0] - result[i][0][2][0]
        arr.append(distance)
        # print(arr)
        if distance < 13:
            temp1 = result[i][1]
            temp1 = temp1.split()
            temp2 = result[i+1][1]
            temp2 = temp2.split()
            temp1 += temp2
            temp1 = " ".join(temp1)
            temp = list(result[i])
            temp[1] = temp1
            temp = tuple(temp)
            result[i]=temp
            result[i][0][1] = result[i+1][0][1]
            result[i][0][2] = result[i+1][0][2]
            result.pop(i+1)
            i-=1
        i+=1
        if i==len(result)-1:
            break
    return result, arr

def time_bbox(result):
    count_2 = 0
    arr_tx = []
    arr_bx = []
    arr_bx_arr = []
    arr_tx_arr = []
    arr_distance = []
    # show video
    for (coord, text, prob) in result:
        (topleft, topright, bottomright, bottofleft) = coord
        tx, ty = (int(topleft[0]), int(topleft[1]))
        bx, by = (int(bottomright[0]), int(bottomright[1]))
        #cv2.rectangle(frame_2, (tx, ty), (bx, by), (0, 0, 255), 2)
        count_2 += 1
        arr_bx.append(bx)
        arr_tx.append(tx)

        for i in range(count_2-1):
            arr_bx_arr.append(arr_bx[i])
            arr_tx_arr.append(arr_tx[i])
    # print("len arr_tx:", len(arr_tx))
    # print("len arr_bx:", len(arr_bx))
    
    for i in range(len(arr_tx)):
        distance = arr_bx[i] - arr_tx[i]
        # print("distance : ",distance)
        arr_distance.append(distance)

    # if (len(arr_tx_arr)) == 1:
    #     distance = arr_tx_arr[0] - arr_bx_arr[0]
    #     #print("jarak drawing bound : ",distance)
    #     arr_distance.append(distance)
    # elif (len(arr_tx_arr)) > 1:
    #     for j in range(len(arr_tx_arr)):
    #         if j != 0:
    #             distance = arr_tx_arr[j] - arr_bx_arr[j]
    #             #print(f"jarak drawing bound ke -{j} : {distance}")
    #             arr_distance.append(distance)
    return arr_distance


def bounding_box(result,frame_2):
    # cek bounding box
    count_2 = 0
    arr_tx = []
    arr_bx = []
    arr_bx_arr = []
    arr_tx_arr = []
    arr_distance = [0]
    # show video
    for (coord, text, prob) in result:
        (topleft, topright, bottomright, bottofleft) = coord
        tx, ty = (int(topleft[0]), int(topleft[1]))
        bx, by = (int(bottomright[0]), int(bottomright[1]))
        cv2.rectangle(frame_2, (tx, ty), (bx, by), (0, 0, 255), 2)
        count_2 += 1
        arr_bx.append(bx)
        arr_tx.append(tx)

    for i in range(count_2-1):
        arr_bx_arr.append(arr_bx[i])
        arr_tx_arr.append(arr_tx[i+1])

    print(arr_tx_arr,arr_bx_arr)
    if (len(arr_tx_arr)) == 1:
        distance = arr_tx_arr[0] - arr_bx_arr[0]
        # print("jarak drawing bound : ",distance)
        arr_distance.append(distance)
    elif (len(arr_tx_arr)) > 1:
        for j in range(len(arr_tx_arr)):
            if j != 0:
                distance = arr_tx_arr[j] - arr_bx_arr[j]
                # print(f"jarak drawing bound ke -{j} : {distance}")
                arr_distance.append(distance)
    return frame_2

def cetak_json(news):
    input_json = []
    j = 0
    jml_berita = len(news)

    for i in range(jml_berita):
        #if ((news[i][0] != "#*") and (news[i][0] != "*") and (news[i][0] != "#")) and (len(news[i][0]) > 1):
            # temp_json = {"text": news[i][0], "start time": news[i][1], "end time": news[i]
            #              [2], "duration": news[i][2] - news[i][1], "repeat": news[i][3]}
        temp_json = {"text": news[i][0], "start time": news[i][1], "end time": 0}
        input_json.append({})
        input_json[j] = temp_json
        j += 1

    with open("out_cnbc.json", "w") as f:
        json.dump(input_json, f, indent=3)
    f.close()

    print("idx j")
    print(j)
    print("jml berita")
    print(jml_berita)


def similar(arr, pjg):
    arr_repetition = []
    arr_text = []
    for i in range(pjg):
        arr_text.append(arr[i][0])

    for i in range(len(arr_text)):
        arr_repetition.append(0)
        for j in range(len(arr_text)):
            if i != j:
                if arr_text[i] == arr_text[j]:
                    arr_text[i] = arr_text[i].upper()
                    arr_text[j] = arr_text[j].upper()
                    arr_repetition[i] += 1

                else:
                    string1 = arr_text[i]
                    string2 = arr_text[j]

                    temp = sm(None, string1, string2)

                    if temp.ratio() > 0.9:
                        if len(arr_text[i]) > len(arr_text[j]):
                            print(f"kalimat 1 : {arr_text[i]}")
                            print(f"kalimat 2 : {arr_text[j]}")
                            print('Similarity Score: ', temp.ratio())
                            arr_text[j] = arr_text[i]
                            arr_text[i] = arr_text[i].upper()
                            arr_text[j] = arr_text[j].upper()
                            arr_repetition[i] += 1

                        elif len(arr_text[i]) < len(arr_text[j]):
                            print(f"kalimat 1 : {arr_text[i]}")
                            print(f"kalimat 2 : {arr_text[j]}")
                            print('Similarity Score: ', temp.ratio())
                            arr_text[i] = arr_text[j]
                            arr_text[i] = arr_text[i].upper()
                            arr_text[j] = arr_text[j].upper()
                            arr_repetition[i] += 1

                        else:
                            print(f"kalimat 1 : {arr_text[i]}")
                            print(f"kalimat 2 : {arr_text[j]}")
                            print('Similarity Score: ', temp.ratio())
                            arr_text[i] = arr_text[i].upper()
                            arr_text[j] = arr_text[j].upper()

        for i in range(pjg):
            arr[i][0] = arr_text[i]

    return arr


def converttimestamp(sec):
    #print('Time in Seconds:', sec)

    td = timedelta(seconds=sec)
    #print('Time in hh:mm:ss:', td)

    str_sec = str(timedelta(seconds=sec))
    return str_sec