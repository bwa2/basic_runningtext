
                temp_news = temp_news.split()
                print("\ntemp_news:")
                print(temp_news)

            temp_news = temp_news[:-1]
            len_temp = len(temp_news)
            if len(news) == 0:
                news = temp_news
            else:
                i = 1
                while (i):
                    if news[-1:] == temp_news[0:1]:
                        news += temp_news[1:]
                        i = 0
                    else:
                        temp_news = temp_news[1:]
                        i=1
                    
            print("\nnews:")
            print(news)

            count = 0
            arr_tx = []
            arr_bx = []
            arr_bx_arr = []
            arr_tx_arr = []
            # show video
            for (coord, text, prob) in result:
                (topleft, topright, bottomright, bottofleft) = coord
                tx, ty = (int(topleft[0]), int(topleft[1]))
                bx, by = (int(bottomright[0]), int(bottomright[1]))
                cv2.rectangle(frame_2, (tx, ty), (bx, by), (0, 0, 255), 2)
                count += 1
                arr_bx.append(bx)
                arr_tx.append(tx)

                for i in range (count-1) :
                    arr_bx_arr.append(arr_bx[i])
                    arr_tx_arr.append(arr_tx [i+1])
            

            if (len(arr_tx_arr)) == 1 :
                distance = arr_tx_arr[0] - arr_bx_arr[0]
                print(f"jarak drawing bound : {distance}")
            elif (len(arr_tx_arr)) > 1 :
                for j in range (len(arr_tx_arr)) :
                    if j != 0 :
                        distance = arr_tx_arr[j] - arr_bx_arr[j]
                        print(f"jarak drawing bound ke -{j} : {distance}")


        

            frame_count += 1
            cv2.imwrite(f'frame_{frame_count}.jpg', frame_2)

        iter += 1
    else:
        break

cap.release()
cv2.destroyAllWindows()