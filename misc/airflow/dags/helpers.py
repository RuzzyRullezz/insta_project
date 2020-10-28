# coding: utf-8
import os

PROJECT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
RUN_PATH = os.path.join(PROJECT_PATH, 'run')
PYTHON_PATH = os.environ.get('PYTHON_PATH', '/usr/bin/python')


def get_python_cmd(script_path):
    script_fullpath = os.path.abspath(os.path.join(RUN_PATH, script_path))
    return f'{PYTHON_PATH} {script_fullpath}'
