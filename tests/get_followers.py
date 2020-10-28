import bootstrap
bootstrap.setup()

from pyctogram.instagram_client import client


def run():
    cl = client.InstagramClient()
    cl.login()
    follower_cnt = 0
    print(follower_cnt)
    followers = cl.get_followers(295116275)
    for fol in followers:
        follower_cnt += len(fol)
        print(follower_cnt)


if __name__ == '__main__':
    run()
