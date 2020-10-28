import os
import sys

import django


def setup():
    django_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                os.pardir, os.pardir, os.pardir))
    sys.path.append(django_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insta_project.settings")
    django.setup()
