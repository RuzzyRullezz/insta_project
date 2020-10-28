from django.conf import settings
from pyctogram.instagram_client.client import InstagramClient, InstagramCheckpointRequired, InstagramChallengeRequired, Instagram5XX
from requests.exceptions import ProxyError

username = settings.LUMINATI_USERNAME
password = settings.LUMINATI_PASSWORD
port = 22225

proxy_url_pattern = f'http://{username}-session-%d:{password}@zproxy.luminati.io:{port}'


def get_valid_ig_client(username, password, log_func=None):
    for i in range(1, 20):
        proxies = {
            'http': proxy_url_pattern % i,
            'https': proxy_url_pattern % i,
        }
        client = InstagramClient(username, password, proxies=proxies,
                                 log_func=log_func, session_file=f'/tmp/{username}_session.dat')
        try:
            client.logged_in = False
            client.login()
            return client
        except (InstagramCheckpointRequired, InstagramChallengeRequired, ProxyError) as exc:
            pass
        except Instagram5XX as exc:
            pass
    raise RuntimeError("Can't get valid ip for luminati.")
