import os
import requests

test_secret = os.environ.get('test_secret')# os.environ['test_secret'] 
print('test_secret is: ', test_secret)
bot_id = os.environ.get('bot_id')# os.environ['bot_id']
chat_id = os.environ.get('chat_id')# os.environ['chat_id']
message = 'test_message'
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
requests.get(api_url)
