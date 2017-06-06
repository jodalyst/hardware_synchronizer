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


CHECKING_PERIOD = 5 #seconds
timing = time.time()
PROCESS_TIMEOUT = 10

lcl = '~/heartbeat'
hal = 'https://eesjs1.net/testsite/hw_supervisor'


while True:
    uname,password = [i.strip() for i in open(os.path.expanduser(lcl+'/.catsoop_login'))]
    payload = {'user': uname, 'pword': password,'command':'status_query'}
    r = requests.get(hal, params=payload)
    print(r.text)
    k = json.loads(r.text)
    if k['state'] ==1:
        payload = {'user': uname, 'pword': password,'command':'hw_command_retrieval'}
        r = requests.post(hal, params=payload)
        print(r)
        k = json.loads(r.text)
        data = k['hw_command']
        p = Popen(['python', '-'],stdin=PIPE,stdout=PIPE,stderr=PIPE)
        print('about to run')
        try:
            outs, errs = proc.communicate(input=data,timeout=PROCESS_TIMEOUT)
            print('got',outs)
            payload['command'] = 'hw_response_provide'
            payload['response'] = outs
            r = requests.post(hal,params=payload)
            print('sent')
        except TimeoutExpired:
            proc.kill()
            payload['action'] = 'test_response'
            payload['response'] = 'TIMEOUT FAILURE'
            r = requests.post(hal,params=payload)
            print('sent with timeout failure')
    while time.time()-timing <CHECKING_PERIOD:
        time.sleep(0.1)
    timing = time.time()
