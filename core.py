from dingding.departInfo import dingUserSync
from dingding.departUser import getdepartUser
from dingding.pinyinzhuan import pinyin_transfer
import json
import requests
from ldap.base import ldapUser
from dingding import msg
import os
import time

DING_URL = "https://oapi.dingtalk.com"
class get_info(dingUserSync):

    def __init__(self):
        self.depart_dict = dingUserSync().get_depart_id()  #获取的是部门name和id的字典
        self.departuser = getdepartUser()  #部门下的成员获取，需要传入部门id
        self.token = dingUserSync().get_token()
    def getSyncInfo(self):
        url = DING_URL + '/user/get?'
        for depart in self.depart_dict:  #获取全部部门的id
            '''
            组名称: pinyin_transfer(depart)
            组内所有人员： departuser.get_depart_user(depart_dict[depart]) 
            返回值如下：
            当前同步的是yizu
            [{'name': '马琳', 'userid': '09495332351255239'}, {'name': '陈伟', 'userid': '03035330641212887'}]
            '''
            print('##### 当前同步的是{} #####'.format(pinyin_transfer(depart)))
            # print(self.departuser.get_depart_user(self.depart_dict[depart]))
            for user in self.departuser.get_depart_user(self.depart_dict[depart]):
                '''
                可取两个值：{'name':'崔建哲','userid':'598941324'}
                '''
                # print(useralias)
                param_dict = {
                    'access_token': self.token,
                    'userid': user.get('userid')
                }
                userinfo_res = json.loads(requests.get(url, param_dict).text)
                username = str(userinfo_res.get('email')).rsplit('@')[0] #截取邮箱字段前缀哦
                if username == '' or username == 'None' or username is None:  #刚入职人员无邮箱跳过此次循环
                    continue
                else:
                    listUser.append(username)
                    # print(username)
                    useralias = user.get('name')
                    # listname.append(pinyin_transfer(useralias))  #名字转拼音模块
                    userid = user.get('userid')
                    departname = pinyin_transfer(depart)
                    # listDepart.append(departname)
                    print('\033[0;32;40m username：{},userid:{},useralias：{},departname：{} \033[0m'.format(username,userid,useralias,departname))
                    ldapUser(username=username,useralias=useralias,userid=userid,departName=departname).searchUser()

def deleteDepartUser():
    whiteList = ['yingyuzu']
    for depart in listDepart:
        if depart not in whiteList:
            ldapUser(username=None,useralias=None, userid=None, departName=depart).delete_Depart_User()

def leaveInfo():
    filePath = '/alidata/scripts/ldap/log/users/old_user/'
    if "userOld" in os.listdir(filePath):
        with open(filePath + 'userOld', 'r', encoding='utf-8') as oldname:
            oldListName = oldname.read().split(',')
        addName = [nameValue for nameValue in listUser if nameValue not in oldListName] #新增 注：只是对比文件里面的的数据与阿里云人员列表数据
        leaveName = [nameValue for nameValue in oldListName if nameValue not in listUser] #离职 不对比ldap中的旧账户
        if len(oldListName) > 1400 and len(leaveName) > 0:
            for user in leaveName:
                ldapUser(username=user, useralias=None, userid=None, departName=None).deleteLdapUser()  # 删除离职账号
            delete_msg = '**LDAP离职人员账户删除通知**:' + '\n\n' + \
                         '**当前时间**:' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n\n' + \
                         '**删除账号列表**:' + str(leaveName)
            msg.send_msg(delete_msg)
        if len(addName) > 0:
            add_msg = '**LDAP入职人员账户新增通知**:' + '\n\n' + \
                         '**当前时间**:' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n\n' + \
                         '**新增账号列表**:' + str(addName)
            msg.send_msg(add_msg)

        with open(filePath + 'userOld', 'w', encoding='utf-8') as nameinfo:  #更新本地info
            nameinfo.write(','.join(listUser))

    else:
        with open(filePath + 'userOld', 'w', encoding='utf-8') as nameinfo:
            nameinfo.write(','.join(listUser))


if __name__ == '__main__':
    with open('./ldap/zu', 'r') as depart:
        listDepart = depart.read().split('\n')[:-1]  #zu名称集成本地
    listUser = [] #存储邮箱前缀
    # listname = [] #存储name字段转拼音
    # listDepart = [] #存储部门名称
    syncStart = get_info().getSyncInfo() #同步新增账号操作
    # aliAllUser = list(set(listUser + listname))
    leaveInfo()
    # deleteDepartUser()  #删除组里过期的人员，不用经常执行，看情况执行