#date:2018/6/27

import os,sys,paramiko
import re

def put_file(file,destination_file,ip,user,passwd):
    msg={}
    t = paramiko.Transport((ip, 22))
    print(file,destination_file,ip,user,passwd)
    try:
        t.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        #获取filename
        ret = file.split('/')
        file_name = ret[-1]
        destination_path = os.path.join(destination_file,file_name)
        sftp.put(file, destination_path)
        t.close()
        result = ''.join([destination_path,'上传成功'])
        msg['ip'] = ip
        msg['result'] = result
    except Exception as e:
        print(e,1111111111)
        msg['ip'] = ip
        msg['result'] = e
    return msg



ret = put_file('123','456','10.0.1.30','root','zentech')
print(ret)