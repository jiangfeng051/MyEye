#date:2018/6/26

import getpass,os
import pymysql

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyEye.settings")
from django.conf import settings
# print(settings.PY_MYSQL_CONN_DICT)
class DbConnect:
    def __init__(self):
        self.__conn_dict=settings.PY_MYSQL_CONN_DICT
        self.conn = None
        self.cursor = None

    def connect(self,cursor=pymysql.cursors.DictCursor):
        self.conn = pymysql.connect(**self.__conn_dict)
        self.cursor = self.conn.cursor(cursor=cursor)
        return self.cursor

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

