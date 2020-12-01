from dingding.departInfo import dingUserSync
from dingding.departUser import getdepartUser
from dingding.pinyinzhuan import pinyin_transfer
import json
import requests
from ldap.deleteDepartUser import *
from dingding import msg
import os
import time

DING_URL = "https://oapi.dingtalk.com"
class get_info(dingUserSync):

    def __init__(self):
        self.depart_dict = dingUserSync().get_depart_id()  #获取的是部门name和id的字典
        self.departuser = getdepartUser()  #部门下的成员获取，需要传入部门id
        self.token = dingUserSync().get_token()
    def getInfo(self):
        url = DING_URL + '/user/get?'
        for depart in self.depart_dict:  #获取全部部门的id
            print(depart)
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
                useralias = pinyin_transfer(user.get('name'))
                listname.append(useralias)
                username = str(userinfo_res.get('email')).rsplit('@')[0] #截取邮箱字段前缀哦
                listUser.append(username)
                departname = pinyin_transfer(depart)
                listDepart.append(departname)

    def leaveInfo(self):
        filePath = './'
        # filePath = '/alidata/scripts/ldap/log/users/old_user/'
        if "userOld" in os.listdir(filePath):
            with open(filePath + 'userOld', 'r', encoding='utf-8') as oldname:
                oldListName = oldname.read().split(',')[:-1]
            addName = [nameValue for nameValue in listUser if nameValue not in oldListName] #新增
            leaveName = [nameValue for nameValue in oldListName if nameValue not in listUser] #离职
            print(addName)
            print(leaveName)
            if len(oldListName) > 1000 and len(leaveName) > 0:
                # for user in leaveName:
                #     ldapUser(username=user, useralias=None, userid=None, departName=None).deleteLdapUser()  # 删除离职账号
                delete_msg = '**LDAP账户删除通知**:' + '\n\n' + \
                             '**当前时间**:' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n\n' + \
                             '**删除账号列表**:' + str(leaveName)
                msg.send_msg(delete_msg)
            if len(addName) > 0:
                add_msg = '**LDAP账户新增通知**:' + '\n\n' + \
                             '**当前时间**:' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n\n' + \
                             '**新增账号列表**:' + str(addName)
                msg.send_msg(add_msg)

            with open(filePath + 'userOld', 'w', encoding='utf-8') as nameinfo:  #更新本地info
                for newinfo in listUser:
                    nameinfo.write(str(newinfo + ','))

        else:
            with open(filePath + 'userOld', 'w', encoding='utf-8') as nameinfo:
                for newinfo in listUser:
                    nameinfo.write(str(newinfo + ','))
    def deleteDepartUser(self):
        for depart in listDepart:  # 获取全部部门的id
            delete_Depart_User(depart)


if __name__ == '__main__':
    listUser = list()
    listname = list()
    # listDepart = list()
    with open('./ldap/zu','r',encoding='utf-8') as zu:
        listDepart = list(set(zu.read().split('\n')[:-1]))
    syncStart = get_info()
    syncStart.getInfo()

    aliyunAllUser = list(set(listUser + listname))
    with open('./alialluser','w',encoding='utf-8') as ali:
        for i in aliyunAllUser:
            ali.write(str(i + ','))

    print(aliyunAllUser)
    syncStart.deleteDepartUser()
      #ldap系统里面所有的用户信息
    alluser = ldapAlluser
    with open('./ldapalluser','w',encoding='utf-8') as ali:
        for i in alluser:
            ali.write(str(i + ','))
    shanuser = [user for user in alluser if user not in aliyunAllUser]
    print(shanuser)
    with open('./delUser', 'w', encoding='utf-8') as name:
        for user in shanuser:
            name.write(str(user + ','))
