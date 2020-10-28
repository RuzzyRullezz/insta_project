import json
import os
import random
import sys
import shutil

from pyctogram.instagram_client.client import InstagramClient, web
from pyctogram.instagram_client.exceptions import InstagramChallengeRequired, InstagramCheckpointRequired, InstagramAccountHasBeenDisabled
from transliterate import translit
from google_images_download import google_images_download

from imap_client.get_mail import get_verify_link, mark_all_read
from onlinesim.exceptions import NoSmsCode

from promo_bots.browser import CheckpointChallenger, Register
from promo_bots.client import IgClient
from promo_bots.prepare import prepare_bot
from yandex_connect.users import create_user
from onlinesim import api as onlinesim_api

from database.models import Accounts

names_file = os.path.join(os.path.dirname(__file__), 'names', 'names.txt')
images_dir = os.path.join(os.path.dirname(__file__), 'images')
images_used_dir = os.path.join(os.path.dirname(__file__), 'images_used')
if sys.platform in ('linux', 'linux2'):
    driver_dir = 'linux'
elif sys.platform == "darwin":
    driver_dir = 'mac'
else:
    raise RuntimeError("Unsupported platform")
chrome_driver = os.path.join(os.path.dirname(__file__), os.path.pardir, 'drivers', driver_dir, 'chromedriver')


def get_random_name():
    with open(names_file, 'r') as rf:
        names = list(map(lambda n: n.strip(), rf.readlines()))
    random_name = random.choice(names)
    return random_name


def get_translit(s):
    return translit(s, reversed=True).replace('\'', '')


def download_owl_images():
    response = google_images_download.googleimagesdownload()
    response.download({
        'keywords': '"owl avatar"',
        'limit': 1000,
        'output_directory': images_dir,
        'no_directory': True,
        'chromedriver': chrome_driver,
    })


def get_random_profile_pic():
    filelist = []
    for dirpath, _, filenames in os.walk(images_dir):
        for f in filenames:
            filelist.append(os.path.abspath(os.path.join(dirpath, f)))
    return random.choice(filelist)


def move_pic_to_used(img_path):
    if not os.path.exists(images_used_dir):
       os.mkdir(images_used_dir)
    new_path = os.path.join(images_used_dir, os.path.basename(img_path))
    shutil.move(img_path, new_path)


def generate_account(old_username, old_password):
    domain = 'ruzzy.pro'
    sova_timofey = Accounts.objects.get(username='sova_timofei')
    biography = f'Понравилось? Переходи на основной профиль - @{sova_timofey.username}'
    phone = None
    new_surname = 'Сова'
    attempts = 0
    max_attempts = 100
    while True:
        attempts += 1
        new_name = get_random_name()
        new_username = get_translit(f'{new_surname}_{new_name}'.lower())
        if web.username_is_ok(new_username) and not Accounts.objects.filter(username=new_username).exists():
            break
        else:
            if attempts >= max_attempts:
                raise RuntimeError("Can't get random username")
    new_email = f'{new_username}@{domain}'
    new_email_password = sova_timofey.email_password
    gender = 1
    create_user(new_surname, new_name, new_email, new_email_password)
    print(f"Created yandex user: {new_surname} {new_name} - {new_email}")
    client = IgClient(
        old_username,
        old_password,
        new_email,
        new_email_password,
    )
    client.login()
    client.edit_profile(new_username, new_email, gender, first_name=f'{new_surname} {new_name}', biography=biography)
    print(f"Updated IG data: {old_username} -> {new_username}")

    new_profile_pic = get_random_profile_pic()
    client.change_profile_picture(new_profile_pic)
    move_pic_to_used(new_profile_pic)
    mark_all_read(new_email, new_email_password)
    client.send_confirm_email()
    verify_link = get_verify_link(new_email, new_email_password)
    response = client.get_session().get(verify_link)
    if response.status_code != 200:
        raise RuntimeError("Can't get to verify link")
    new_password = sova_timofey.password
    if old_password != new_password:
        client.change_password(new_password)
    if phone is None:
        max_attempts = 10
        attempts = 0
        while True:
            try:
                attempts += 1
                tzid, phone = onlinesim_api.get_tzid_phone(owner_username=new_name)
                client.send_sms_code(phone)
                code = onlinesim_api.get_sms(tzid)
                client.verify_sms_code(phone, code)
                onlinesim_api.set_operation_ok(tzid)
                break
            except NoSmsCode:
                if attempts >= max_attempts:
                    raise
                else:
                    continue
        print(f"Get phone: {phone}")
    new_account = Accounts.objects.create(
        username=new_username,
        password=new_password,
        email=new_email,
        email_password=new_email_password,
        phone=phone,
    )
    print("Account saved in DB")
    prepare_bot(new_account)


def check_accounts(accounts_filename, sep=':'):
    with open(accounts_filename, 'r') as rf:
        account_password_list = list(map(lambda a: (a.split(sep)[0], a.split(sep)[1]), rf.readlines()))
    for username, password in account_password_list:
        try:
            InstagramClient(username, password).login()
        except InstagramAccountHasBeenDisabled:
            continue
        except (InstagramCheckpointRequired, InstagramChallengeRequired):
            print(f'{username}:{password}:checkpoint')
        print(f'{username}:{password}:clear')


def generate_accounts_from_file(accounts_filename, sep=':'):
    with open(accounts_filename, 'r') as rf:
        account_password_list = list(map(lambda a: (a.split(sep)[0], a.split(sep)[1], a.split(sep)[2]), rf.readlines()))
        for username, password, status in account_password_list:
            generate_account(username, password)


def register(proxy_protocol=None, proxy_ip=None, proxy_port=None):
    domain = 'ruzzy.pro'
    sova_timofey = Accounts.objects.get(username='sova_timofei')
    biography = f'Понравилось? Переходи на основной профиль - @{sova_timofey.username}'
    new_surname = 'Сова'
    attempts = 0
    max_attempts = 100
    while True:
        attempts += 1
        new_name = get_random_name()
        new_username = get_translit(f'{new_surname}_{new_name}'.lower())
        if web.username_is_ok(new_username) and not Accounts.objects.filter(username=new_username).exists():
            break
        else:
            if attempts >= max_attempts:
                raise RuntimeError("Can't get random username")
    new_email = f'{new_username}@{domain}'
    new_email_password = sova_timofey.email_password
    gender = 1
    create_user(new_surname, new_name, new_email, new_email_password)
    print(f"Created yandex user: {new_surname} {new_name} - {new_email}")
    first_name = f'{new_surname} {new_name}'
    new_password = sova_timofey.password
    phone = Register(first_name, new_username, new_password, new_email, new_email_password,
                     proxy_protocol=proxy_protocol, proxy_ip=proxy_ip, proxy_port=proxy_port).reg()
    print(f"Created IG user: {new_username}")
    proxies = {'https': f'{proxy_protocol}{proxy_ip}:{proxy_port}'}
    new_account = Accounts.objects.create(
        username=new_username,
        password=new_password,
        email=new_email,
        email_password=new_email_password,
        phone=phone,
    )
    print("Account saved in DB")
    client = new_account.get_bot_client()
    client.client.session.proxies = proxies
    client.login()
    client.client.edit_profile(new_username, new_email, gender, first_name=first_name, biography=biography)
    new_profile_pic = get_random_profile_pic()
    client.client.change_profile_picture(new_profile_pic)
    move_pic_to_used(new_profile_pic)
    print("Change profile photo")
    mark_all_read(new_email, new_email_password)
    client.client.send_confirm_email()
    verify_link = get_verify_link(new_email, new_email_password)
    response = client.client.session.get(verify_link)
    if response.status_code != 200:
        raise RuntimeError("Can't get to verify link")

    prepare_bot(new_account, force_proxy=proxies)
    return new_account
