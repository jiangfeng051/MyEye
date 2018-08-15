#date:2018/7/3
import paramiko,os


def execute(cmd,ip,user,passwd):
    msg={}
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip,22,user,passwd)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        #stdout.read(),stderr.read()只能读取一次数据，第二次在读取的时候会为空
        result_stdout = str(stdout.read(), 'utf-8')
        print(result_stdout)
        result_stderr = str(stderr.read(), 'utf-8')
        if result_stdout:
            msg['result'] = result_stdout
        else:
            msg['result'] = result_stderr
        msg['ip']=ip
    except Exception as e:
        msg['ip'] = ip
        msg['result'] = '连接失败,请检查'
    return msg

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
        msg['ip'] = ip
        msg['result'] = str(e)
    return msg

def callback(future):
    print(future.result())


