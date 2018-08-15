#date:2018/8/10
import time
import random

def ruleid_create():
    timestamp_str = str(round(time.time()*10000000))
    a = []
    for i in range(5):
        a.append(str(random.randint(1, 9)))

    random_nu = ''.join(a)
    rule_id = ''.join([timestamp_str,random_nu])
    return rule_id

if __name__ == '__main__':
    print(ruleid_create())