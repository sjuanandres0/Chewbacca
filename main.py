import os
import requests

bot_id = os.environ['bot_id']
chat_id = os.environ['chat_id']
message = 'test_message'
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
requests.get(api_url)
