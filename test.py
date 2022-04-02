import time
import os
from datetime import datetime
import requests

start_tmsp = datetime.now()
bot_id = os.environ.get('bot_id')
chat_id = os.environ.get('chat_id')
machine = 'server'
if bot_id == None:
    import config.cred as cred
    bot_id = cred.bot_id
    chat_id = cred.chat_id
    machine = 'laptop'

message = 'Start {}'.format(start_tmsp)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
requests.get(api_url)

while True:
    time.sleep(300) 
    end_tmsp = datetime.now()
    elapsed_sec = (end_tmsp - start_tmsp).seconds
    print(elapsed_sec, '-', end_tmsp)

    message = 'Ran {}\nElapsed {}secs\nEnd_tmsp {}'.format(machine, elapsed_sec, end_tmsp)
    api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
    requests.get(api_url)
