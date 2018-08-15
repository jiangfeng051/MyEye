#date:2018/6/26
import getpass,os,subprocess,time
from dbutils.connectdb import DbConnect
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyEye.settings")



class UserPortal:
    def __init__(self):
        self.user = None
        self.db_conn = DbConnect()

    def user_auth(self):
        retry_count = 0
        while retry_count<3:
            username = input('用户名：').strip()
            if len(username)==0:continue
            passwd = input("密码:").strip()
            if len(passwd)==0:
                print('passwd cannot be null')
                continue
            cursor = self.db_conn.connect()
            sql = """
                select user_id,username,passwd,status from 
                  user_info where username=%s and passwd=%s
            """
            cursor.execute(sql, [username, passwd])
            result = cursor.fetchone()
            print(result)
            self.db_conn.close()
            if result:
                self.user=result
                return
            else:
                retry_count +=1
                print('Ivalid username or passwd')
                continue
        else:
            exit('too many attempts')

    #生成操作日志的文件夹,返回日志存在放的相对路径
    #生成的时间应该为本地时间，修改settings的时区配置，默认是UTC，改为Asia/Shanghai
    def login_log(self):
        current_time = time.localtime()
        dir_name = time.strftime('%Y%m%d',current_time)
        log_time = int(time.strftime('%Y%m%d%H%M%S', current_time))
        log_name = '%s.%s' % (str(log_time), 'log')
        print(time.strftime('%Y%m%d%H%M%S',current_time))
        log_date_path = os.path.join('logs',dir_name)
        if os.path.exists(log_date_path):
            print(log_date_path)
        else:
            os.makedirs(log_date_path)
        log_path = os.path.join(log_date_path, log_name)
        print(log_path)
        return log_path

    def interactive(self):
        self.user_auth()
        if self.user:
            #列出当前用户下的所有主机组
            while True:
                cursor = self.db_conn.connect()
                sql = """
                    select 
                      host_group.group_name,
                      host_group.group_id 
                    from user_info ,user_group_detail ,host_group 
                    where user_info.user_id=user_group_detail.user_id 
                    and user_group_detail.group_id=host_group.group_id 
                    and user_info.user_id=%s
                """
                cursor.execute(sql,[self.user['user_id']])
                result_group = cursor.fetchall()
                self.db_conn.close()
                print(result_group)
                result_group_len=len(result_group)
                for index,host_group in enumerate(result_group,1):
                    print('%s.%s'%(index,host_group['group_name']))
                #选择主机组
                choose_group = input('choose group:').strip()
                if len(choose_group)==0:continue
                if not choose_group.isdigit():
                    print('please input a number')
                    continue
                choose_group = int(choose_group)
                if choose_group>result_group_len:
                    print('invalid host group')
                    continue
                result_group_choose = result_group[choose_group-1]
                # print(result_group_choose)
                #列出当前主机组下的所有主机
                while True:
                    cursor = self.db_conn.connect()
                    sql = """
                        select host.host_name,
                                host.ip_addr,
                                host_group.group_name,
                                host_user.user_name,
                                host_user.passwd 
                        from host_group,host_group_detail,host,host_user
                        where host_group.group_id=host_group_detail.group_id 
                        and host_group_detail.host_id=host.host_id 
                        and host.host_user_id=host_user.host_user_id 
                        and host_group.group_id=%s
                    """
                    cursor.execute(sql,[result_group_choose['group_id']])
                    result_host = cursor.fetchall()
                    # print(result_host)
                    self.db_conn.close()
                    result_host_len = len(result_host)
                    for index,host in enumerate(result_host,1):
                        print('%s.%s:%s:%s'%(index,host['host_name'],host['ip_addr'],host['user_name']))
                    #选择主机
                    choose_host = input('choose host:')
                    if len(choose_host) == 0: continue
                    if choose_host=='b':break
                    if not choose_host.isdigit():
                        print('please input a number')
                        continue
                    choose_host = int(choose_host)
                    if choose_host > result_host_len:
                        print('invalid host')
                        continue
                    result_host_choose = result_host[choose_host-1]
                    # print(result_host_choose)
                    log_path = self.login_log()
                    #用户名和日志路径保存到数据库
                    cursor = self.db_conn.connect()
                    sql = """
                        insert into session_log_detail (user_id,username,log) values (%s,%s,%s)
                    """
                    cursor.execute(sql,[self.user['user_id'],self.user['username'],log_path])
                    self.db_conn.close()
                    login_cmd = 'sshpass -p {passwd} ssh {user}@{ip} -o StrictHostKeyChecking=no | tee -a {log}'.format(
                        passwd=result_host_choose['passwd'],user=result_host_choose['user_name'],
                        ip=result_host_choose['ip_addr'],log = log_path
                    )
                    ssh_instance = subprocess.run(login_cmd,shell=True)








if __name__ == '__main__':
    portal = UserPortal()
    portal.interactive()

