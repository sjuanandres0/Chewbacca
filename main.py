import os
import requests

test_secret = os.environ.get('TEST_SECRET')# os.environ['test_secret'] 
print('test_secret is: ', test_secret)
bot_id = os.environ.get('BOT_ID')# os.environ['bot_id']
chat_id = os.environ.get('CHAT_ID')# os.environ['chat_id']
message = 'test_message'
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
requests.get(api_url)
