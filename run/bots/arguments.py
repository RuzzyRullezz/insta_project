import argparse


def get_username():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Account username", type=str)
    return parser.parse_args().username

