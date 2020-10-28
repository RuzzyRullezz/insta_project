import os
from logging import handlers


class GroupOtherWriteRotatingFileHandler(handlers.RotatingFileHandler):

    def _open(self):
        default_umask = 0o002
        try:
            os.umask(0o115)  # u+rw g+rw o+w
            rtv = super(GroupOtherWriteRotatingFileHandler, self)._open()
            return rtv
        finally:
            os.umask(default_umask)
