import schedule
import time

def show_name():
    print("The code is running\n")

schedule.every(4).seconds.do(show_name)

while 1:
    schedule.run_pending()
    time.sleep(1)

# we will use this to run the correlation scanner and send email alerts