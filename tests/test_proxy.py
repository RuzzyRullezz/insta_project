import requests


def run():
    get_ip_url = 'http://icanhazip.com/'
    uri = '80.241.219.59:3129'
    proxies = dict(
        http=f'http://{uri}',
        https=f'https://{uri}',
    )
    response = requests.get(get_ip_url, proxies=proxies, timeout=10)
    print(f'Response: {response.text}\n')



if __name__ == '__main__':
    run()
