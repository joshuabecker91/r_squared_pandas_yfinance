import schedule
import time

def scheduled_function():
    print("The code is running\n")

schedule.every(4).seconds.do(scheduled_function)

while 1:
    schedule.run_pending()
    time.sleep(1)

# we will use this to run the correlation scanner and send email alerts