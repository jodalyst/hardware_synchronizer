import requests
from subprocess import Popen, PIPE
import datetime
import time
import os


CHECKING_PERIOD = 5 #seconds
timing = time.time()

lcl = '~/heartbeat'

while True:
    uname,password = [i.strip() for i in open(os.path.expanduser(lcl+'/.catsoop_login'))]
    payload = {'user': uname, 'pword': password}
    r = requests.get('https://eesjs1.net/testsite/hw_supervisor', params=payload)
    print(r.text)
    while time.time()-timing <CHECKING_PERIOD:
        time.sleep(0.1)
    timing = time.time()
