#date:2018/7/11
import getpass,os,subprocess,time



def filename():
    current_time = time.localtime()
    # dir_name = time.strftime('%Y%m%d', current_time)
    backendfiles_time = int(time.strftime('%Y%m%d%H%M%S', current_time))
    backendfiles_name = str(backendfiles_time)
    print(time.strftime('%Y%m%d%H%M%S', current_time))
    backendfiles_date_path = os.path.join('backendfiles', backendfiles_name)
    if os.path.exists(backendfiles_date_path):
        print(backendfiles_date_path)
    else:
        os.makedirs(backendfiles_date_path)
    print(backendfiles_date_path)
    return backendfiles_date_path


