from django.conf import settings

from .browser import ConnectWeb


def create_user(name, surname, email, password):
    ya_connect_client = ConnectWeb(settings.YA_CONNECT_USER, settings.YA_CONNECT_PASSWORD)
    username, domain = email.split('@')
    ya_connect_client.add_mail(domain, surname, name, username, password)
