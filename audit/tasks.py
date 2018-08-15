#date:2018/6/20

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from backend.executecmd import execute
from backend.executecmd import put_file
from concurrent.futures import ThreadPoolExecutor
from gevent.pool import Pool
import gevent



@shared_task
def multi_cmd(cmd,hsot_msg):
    result_list = []
    pool = ThreadPoolExecutor(5)
    for host in hsot_msg:
        ret = pool.submit(execute, cmd=cmd, ip=host['ip_addr'], user=host['user_name'], passwd=host['passwd'])
        result_list.append(ret.result())
    pool.shutdown(wait=True)
    return result_list

@shared_task
def multi_cmd_gevent(cmd,hsot_msg):
    result_list = []
    pool = Pool(None)
    for host in hsot_msg:
        ret = pool.spawn(execute, cmd=cmd, ip=host['ip_addr'], user=host['user_name'], passwd=host['passwd'])
        #获取返回值的类型，所有的方法，值，状态
        # print(type(ret),dir(ret),ret.get(),ret.successful())
        result_list.append(ret.get())
    pool.join()
    return result_list

@shared_task
def multi_put_file(files_list,hsot_msg,destination_file,):
    result_list = []
    pool = Pool(None)
    for host in hsot_msg:
        for file in files_list:
            ret = pool.spawn(put_file, file=file,destination_file=destination_file, ip=host['ip_addr'], user=host['user_name'], passwd=host['passwd'])
            result_list.append(ret.get())
    pool.join()
    return result_list



@shared_task
def add(x, y):
    return x + y
