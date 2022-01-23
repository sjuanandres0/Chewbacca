import requests

#bot_id = 'bot_id_test'
#chat_id = 'chat_id_test'
message = 'test_message'
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_id, chat_id, message)
print(api_url)
requests.get(api_url)