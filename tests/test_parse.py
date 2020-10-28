import bootstrap
bootstrap.setup()

from profiles_getters.followers_getters import get_profile_followers


def run():
    target_username = 'gus__original'
    for users_pack in get_profile_followers(target_username):
        print(users_pack)


if __name__ == '__main__':
    run()

