import requests
import config.cred as cred

bot_id = cred.bot_id
chat_id = cred.chat_id

message = '<b>test_message</b><a href="https://chewbacca22.herokuapp.com/">Dashboard</a>'
#message = 'Running Main...'#\nCheck: {}'.format(chewie_url)
api_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=HTML'.format(bot_id, chat_id, message)
requests.get(api_url)
