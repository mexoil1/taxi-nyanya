import requests
from django.conf import settings


def send_tg_message(message):
    requests.get(
        f'https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage?chat_id={settings.TG_CHAT_ID}&text={message}&parse_mode=markdown')
