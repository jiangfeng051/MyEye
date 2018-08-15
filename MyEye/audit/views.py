from django.shortcuts import render,HttpResponse,redirect
from dbutils.connectdb import DbConnect
from backend.filename import filename
from backend.page import PageHelp
from backend.idcreate import ruleid_create
import json,os
from concurrent.futures import ThreadPoolExecutor
from backend.executecmd import execute,callback
from audit import tasks
from celery.result import AsyncResult
from celery.task.control import revoke

# Create your views here.

def login(request):
    message = ""
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = 'select user_id,username,passwd,status from user_info where username=%s and passwd=%s'
        cursor.execute(sql,[username,passwd])
        result = cursor.fetchone()
        print(result)
        db_conn.close()
        if result:
            request.session['is_login'] = True
            request.session['user_id'] = result['user_id']
            request.session['username'] = username
            return redirect('index.html')
        else:
            message= "用户名或密码错误"
        obj = render(request,'login.html',{'msg':message})
        return obj


def auth(func):
    def inner(request,*args,**kwargs):
        is_login=request.session.get('is_login')
        if is_login:
            return func(request,*args,**kwargs)
        else:
            return redirect('/login.html')
    return inner

@auth
def index(request):
    return render(request,'index.html')

@auth
def multi_cmd(request):
    host_dic={}
    if request.method == 'GET':
        user_id= request.session.get('user_id')
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
            select user_group_detail.group_id,
                   host_group.group_name
            from user_info ,user_group_detail ,host_group
            where user_info.user_id=user_group_detail.user_id
            and user_group_detail.group_id=host_group.group_id 
            and user_info.user_id=%s
        """
        cursor.execute(sql, [user_id])
        result_group = cursor.fetchall()
        print(result_group)
        if result_group:
            #获取每个组下所有的主机
            for group in result_group:
                sql="""
                    select host.host_id,host.host_name,host.ip_addr 
                    from host,host_group,host_group_detail
                    where host_group.group_id=host_group_detail.group_id
                    and host_group_detail.host_id=host.host_id
                    and host_group.group_id=%s
                """
                cursor.execute(sql,[group['group_id']])
                result_host = cursor.fetchall()
                host_dic[group['group_name']]=result_host
            # print(host_dic)
        return render(request,'multi_cmd.html',{'host_dic':host_dic})
    elif request.method=='POST':
        data = {'status':True,'error':"",'message':''}
        print(request.POST)
        host_list = request.POST.get('host_list')
        cmd = request.POST.get('cmd').strip()
        if len(host_list)==0 or len(cmd)==0:
            data['error']='主机或者cmd命令为空，请检查'
            data['status'] = False
            return HttpResponse(json.dumps(data))
        else:
            #根据分隔符，获取所有需要执行的host_id
            host_list = host_list.split(',')
            print(host_list)
            #获取所有host的ip，port，user，passwd
            db_conn = DbConnect()
            cursor = db_conn.connect()
            sql = """
                select host.ip_addr,host.port,host_user.user_name,host_user.passwd 
                from host ,host_user where host.host_user_id=host_user.host_user_id 
                and host.host_id in %s
            """
            cursor.execute(sql, [host_list])
            hsot_msg = cursor.fetchall()
            print(hsot_msg)
        #     #--------------启动多线程执行cmd---------------------
        #     pool = ThreadPoolExecutor(5)
        #     for host in hsot_msg:
        #         ret = pool.submit(execute,cmd=cmd,ip=host['ip_addr'],user=host['user_name'],passwd=host['passwd'])
        #         result_list.append(ret.result())
        #     pool.shutdown(wait=True)
        #     data['message'] = result_list
        #     print(result_list)
        # return HttpResponse(json.dumps(data))
            #-------------celery执行多线程cmd---------------------
            # ret = tasks.multi_cmd.delay(cmd,hsot_msg)
            #-------------celery执行协程cmd---------------------
            ret = tasks.multi_cmd_gevent.delay(cmd,hsot_msg)
            print(type(ret),ret.task_id)
            data['message'] = ret.task_id
            return HttpResponse(json.dumps(data))


@auth
def multi_task_result(request):
    data = {'status': True, 'error': "", 'message': ''}
    task_id = request.POST.get('task_id')
    ret_status = AsyncResult(task_id).successful()
    if ret_status:
        ret_cmd = AsyncResult(task_id).get()
        print(ret_cmd)
        data['message'] = ret_cmd
    else:
        data['status'] = False
    return HttpResponse(json.dumps(data))

@auth
def multi_task_cancel(request):
    data = {'status': True, 'error': "", 'message': ''}
    task_id = request.POST.get('task_id')
    print(task_id)
    if task_id:
        revoke(task_id, terminate=True)
        data['message'] = '任务已经终止'
    else:
        data['status'] = False
        data['error'] = '当前没有任务在执行'
    return HttpResponse(json.dumps(data))

def celery_test(request):
    res = tasks.add.delay(6,999)
    print(res.task_id,dir(res))
    return HttpResponse(res.task_id)


@auth
def multi_file(request):
    host_dic = {}
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
                select user_group_detail.group_id,
                       host_group.group_name
                from user_info ,user_group_detail ,host_group
                where user_info.user_id=user_group_detail.user_id
                and user_group_detail.group_id=host_group.group_id 
                and user_info.user_id=%s
            """
        cursor.execute(sql, [user_id])
        result_group = cursor.fetchall()
        print(result_group)
        if result_group:
            # 获取每个组下所有的主机
            for group in result_group:
                sql = """
                        select host.host_id,host.host_name,host.ip_addr 
                        from host,host_group,host_group_detail
                        where host_group.group_id=host_group_detail.group_id
                        and host_group_detail.host_id=host.host_id
                        and host_group.group_id=%s
                    """
                cursor.execute(sql, [group['group_id']])
                result_host = cursor.fetchall()
                host_dic[group['group_name']] = result_host
            # print(host_dic)
        return render(request, 'multi_file.html', {'host_dic': host_dic})
    elif request.method == 'POST':
        data = {'status': True, 'error': "", 'message': ''}
        files_list = []
        files_name_list = []
        files = request.FILES.getlist('file_list')
        file_name = filename()
        for file in files:
            filename_path = os.path.join(file_name,file.name)
            f = open(filename_path,'wb')
            for chunk in file.chunks():
                f.write(chunk)
            f.close()
            files_list.append(filename_path)
            files_name_list.append(file.name)
        host_list = request.POST.get('host_list')
        destination_file = request.POST.get('destination_file')
        if len(host_list)==0 or len(files)==0 or len(destination_file)==0:
            data['error']='主机或者目录或文件为空，请检查'
            data['status'] = False
            return HttpResponse(json.dumps(data))
        # print(destination_file)
        # print(host_list)
        # print(files_list)
        host_list = host_list.split(',')
        print(host_list)
        # 获取所有host的ip，port，user，passwd
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
                        select host.ip_addr,host.port,host_user.user_name,host_user.passwd 
                        from host ,host_user where host.host_user_id=host_user.host_user_id 
                        and host.host_id in %s
                    """
        cursor.execute(sql, [host_list])
        hsot_msg = cursor.fetchall()
        print(files_list,hsot_msg,destination_file,files_name_list)
        db_conn.close()
        ret = tasks.multi_put_file.delay(files_list,hsot_msg,destination_file)
        print(type(ret), ret.task_id)
        data['message'] = ret.task_id
        return HttpResponse(json.dumps(data))


def bootstrap(request):
    return render(request,'bootstrap.html')

@auth
def rule_page(request):
    if request.method == 'GET':
        page = request.GET.get('page')
        page = int(page)
        print(page)
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
            select count(1) as total_count from warning_rule
        """
        cursor.execute(sql)
        total_count_dict = cursor.fetchone()
        total_count = total_count_dict['total_count']
        print(total_count)

        obj = PageHelp(page,total_count,'/rule')
        page_dict = obj.paper_list()
        print(page_dict)
        sql = """
            select rule_id,rule_name,rule_content,rule_condtion,rule_price,rule_time from warning_rule  order by gmt_create desc limit %s,%s
        """
        cursor.execute(sql,[obj.db_start,obj.per_page])
        rule_dict = cursor.fetchall()
        print(rule_dict)
        db_conn.close()

        return render(request,'rule_mointor.html',{'rule_dict':rule_dict,'page_dict':page_dict})

    elif request.method == 'POST':
        data = {'status': True, 'error': "", 'message': ''}
        rule_name = request.POST.get('rule_name')
        rule_content = request.POST.get('rule_content')
        rule_condtion = request.POST.get('rule_condtion')
        rule_price = request.POST.get('rule_price')
        rule_time = request.POST.get('rule_time')
        rule_id = ruleid_create()
        print(rule_name,rule_content,rule_condtion,rule_price,rule_time,rule_id)
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
            insert into warning_rule (rule_id,rule_name,rule_content,rule_condtion,rule_price,rule_time) value (%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql,[rule_id,rule_name,rule_content,rule_condtion,rule_price,rule_time])
        db_conn.close()
        return HttpResponse(json.dumps(data))

@auth
def rule_operation(request):
    if request.method == 'GET':
        rule_id = request.GET.get('rule_id')
        print(rule_id)
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
            select rule_id,rule_name,rule_content,rule_condtion,rule_price,rule_time from warning_rule  where rule_id = %s
        """
        cursor.execute(sql,[rule_id])
        rule_list = cursor.fetchone()
        sql = """
            select rule_log_detail.rule_id,rule_log_detail.result,rule_log_detail.warning,rule_log_detail.gmt_create,warning_rule.rule_name 
            from rule_log_detail ,warning_rule  
            where rule_log_detail.rule_id=warning_rule.rule_id and rule_log_detail.rule_id=%s order by rule_log_detail.gmt_create desc limit 10
        """
        cursor.execute(sql,[rule_id])
        rule_result_dict = cursor.fetchall()
        db_conn.close()
        return render(request,'rule_operation.html',{'rule_list':rule_list,'rule_result_dict':rule_result_dict})
    if request.method == 'POST':
        data = {'status': True, 'error': "", 'message': ''}
        rule_id = request.POST.get('rule_id')
        rule_name = request.POST.get('rule_name')
        rule_content = request.POST.get('rule_content')
        rule_condtion = request.POST.get('rule_condtion')
        rule_price = request.POST.get('rule_price')
        rule_time = request.POST.get('rule_time')
        print(rule_id,rule_name,rule_content,rule_condtion,rule_price,rule_time)
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
            update warning_rule  set rule_name=%s, rule_content=%s, rule_condtion=%s, rule_price=%s, rule_time=%s where rule_id=%s
        """
        cursor.execute(sql,[rule_name,rule_content,rule_condtion,rule_price,rule_time,rule_id])
        db_conn.close()
        return HttpResponse(json.dumps(data))


@auth
def rule_del(request):
    #删除rule规则测试
    if request.method == 'POST':
        data = {'status': True, 'error': "", 'message': ''}
        rule_id = request.POST.get('rule_id')
        db_conn = DbConnect()
        cursor = db_conn.connect()
        sql = """
                    delete from warning_rule where rule_id = %s
                """
        cursor.execute(sql,[rule_id])
        db_conn.close()
        return HttpResponse(json.dumps(data))
