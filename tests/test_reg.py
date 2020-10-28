import bootstrap
bootstrap.setup()

from promo_bots.create_bot import register


if __name__ == '__main__':
    register(proxy_protocol='socks5://', proxy_ip='127.0.0.1', proxy_port=1080)

