import requests
from subprocess import Popen, PIPE, check_output
import datetime
import time
import os
import json
import random
import socket
import string
import multiprocessing
import sys


CHECKING_PERIOD = 5 #seconds
timing = time.time()
PROCESS_TIMEOUT = 10

lcl = '/home/pi/mites17'
hal = 'https://eesjs1.net/testsite/hw_supervisor'


while True:
    print("Here")
    while time.time()-timing <CHECKING_PERIOD:
        print("waiting")
        time.sleep(1)
    timing = time.time()
    uname,password = [i.strip() for i in open(os.path.expanduser(lcl+'/.catsoop_login'))]
    payload = {'user': uname, 'pword': password,'command':'status_query'}
    try:
        print('requesting')
        r = requests.get(hal, params=payload, timeout=1.0)
        print('requested')
        print("requesting at " + str(time.time()))
        print(r.text)
        k = json.loads(r.text)
        if k['state'] in [1, 2]:
            print("must run")
            payload = {'user': uname, 'pword': password,'command':'hw_command_retrieval'}
            r = requests.post(hal, data=payload, timeout=1.0)
            print(r)
            k = json.loads(r.text)
            data = k['hw_command']
            p = Popen(['python', '-'],stdin=PIPE,stdout=PIPE,stderr=PIPE)
            print('about to run')
            try:
                outs, errs = p.communicate(input=data.encode(),timeout=PROCESS_TIMEOUT)
                print('got',outs)
                payload['command'] = 'hw_response_provide'
                payload['hw_resp'] = outs
                r = requests.post(hal,data=payload, timeout=1.0)
                print('sent')
            except:
                p.kill()
                payload['command'] = 'hw_response_provide'
                payload['hw_resp'] = 'TIMEOUT'
                r = requests.post(hal,data=payload, timeout=1.0)
                print('Exception')
                print(sys.exc_info()[0])
    except requests.exceptions.RequestException as e:
        print("CONNECTION ISSUE AT " + str(time.time()))
        print(e)
        pass
    except requests.exceptions.Timeout:
        print("timeout")
        pass
    except requests.exceptions.TooManyRedirects:
        print("crappy url")
        pass
