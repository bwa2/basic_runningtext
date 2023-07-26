from datetime import timedelta

sec = 
print('Time in Seconds:', sec)

td = timedelta(seconds=sec)
print('Time in hh:mm:ss:', td)

str_sec = str(timedelta(seconds=sec))
# Use the below code if you want it in a string
print(str_sec)