import sh
import time
DEPART_LDAP_TPL = """dn: cn={depart_name},ou=group,dc=limikeji,dc=com
objectClass: groupOfUniqueNames
cn: {depart_name}
uniqueMember: uid=test,ou=manager,dc=limikeji,dc=com
"""

USER_LDAP_TPL = """dn: uid={username},ou=manager,dc=limikeji,dc=com
objectClass: top
objectClass: inetOrgPerson
objectClass: posixAccount
givenName: {useralias}
mail: {username}@limikeji.com
uid: {username}
displayName: {useralias}
userPassword: {SSHA}c+4iwEdEZJ4RLfoz1lW8OynwgqclmP4C
description: {useralias}
gidNumber: 1007
uidNumber: {userid}
homeDirectory: /home/{username}
sn: {useralias}
cn: {useralias}
"""

ATTR_MODIFY = """dn: cn={depart_name},ou=group,dc=limikeji,dc=com
changetype: modify
add: uniqueMember
uniqueMember: uid={username},ou=manager,dc=limikeji,dc=com
"""

ATTR_MODIFY_ALL = """dn: cn=Azu,ou=group,dc=limikeji,dc=com
changetype: modify
add: uniqueMember
uniqueMember: uid={username},ou=manager,dc=limikeji,dc=com
"""

ATTR_DELETE_MODIFY = """dn: cn={depart_name},ou=group,dc=limikeji,dc=com
changetype: modify
delete: uniqueMember
uniqueMember: uid={username},ou=manager,dc=limikeji,dc=com
"""

class ldapUser:
    def __init__(self,username,useralias,userid,departName):
        self.username = username
        self.userid = userid
        self.departName = departName
        self.useralias = useralias

    def searchUser(self):
        #由于可能会遇到新入职的老师还没有开通邮箱，此时传入的字段为空，则应该跳过
        if self.username != 'None' and self.username != '' and self.username is not None:
            #添加部门属性ldif文件
            add_DEPART_LDAP_TPL = DEPART_LDAP_TPL.format_map({
                'depart_name': self.departName
            })
            with open('/tmp/temp_depart.ldif', 'w', encoding='utf-8') as file_handler:
                file_handler.write(add_DEPART_LDAP_TPL)
            try:
                departadd_res = sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', '-f', '/tmp/temp_depart.ldif')
                print(departadd_res)
            except sh.ErrorReturnCode_68:
                # 当部门已近存在的时候会触发一个错误的退出，退出的code为68，不过即使重复添加也没有什么问题，因此这里直接pass掉不做任何处理
                pass
            #查询过滤LDAP
            try:
                ldap_res = sh.grep(sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' % self.username),
                        'mail').stdout.decode('utf-8')
            except sh.ErrorReturnCode_1:
                new_USER_LDAP_TPL = USER_LDAP_TPL.format_map({
                        'username':self.username,
                        'userid':str(self.userid).lstrip('0').replace('-','9'),   #因为取钉钉上的userid，但是ldap添加人员信息uid不能0开始，部分userid还有'-'这个符号
                        'useralias':self.useralias,
                        'SSHA':'{SSHA}'
                    })
                with open('/alidata/scripts/ldap/log/users/new_user/new_user_%s' % time.strftime('%Y-%m-%d',time.localtime()), 'a',
                          encoding='utf-8') as file_handler:
                    file_handler.write('新增人员姓名:{},userid:{},useralias:{},departname:{}'.format(self.username,self.userid,self.useralias,self.departName) + '\n')
                with open('/tmp/temp_user.ldif', 'w', encoding='utf-8') as file_handler:
                    file_handler.write(new_USER_LDAP_TPL)
                try:
                    adduser_res = sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', '-f',
                                             '/tmp/temp_user.ldif')
                    # print(adduser_res)
                    # 添加以及更新人员部门属性信息
                    new_ATTR_MODIFY = ATTR_MODIFY.format_map({
                        'depart_name': self.departName,
                        'username': self.username
                    })
                    add_ATTR_MODIFY_ALL = ATTR_MODIFY_ALL.format_map({
                        'username':self.username
                    })
                    with open('/tmp/temp_user_attr_modify.ldif', 'w', encoding='utf-8') as file_handler:
                        file_handler.write(new_ATTR_MODIFY)
                    with open('/tmp/temp_user_Azu.ldif', 'w', encoding='utf-8') as file:  # 添加新增人员到一个大组
                        file.write(add_ATTR_MODIFY_ALL)
                    try:
                        addzu_res = sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', '-f',
                                                '/tmp/temp_user_attr_modify.ldif')
                        # print(addzu_res)
                    except sh.ErrorReturnCode_20 or sh.ErrorReturnCode_20 as error:
                        # ldap_modify: Type or value exists (20)
                        print('\033[0;36;40ml add %s faild Invalid syntax (21)\033[0m'%self.username)
                        print('\033[0;36;40mldap_modify: Type or value exists (20)\033[0m')
                    try:
                        azu_res = sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', '-f',
                                                '/tmp/temp_user_Azu.ldif')
                        # print(azu_res)
                    except sh.ErrorReturnCode_20 as error:
                        # ldap_modify: Type or value exists (20)
                        print('\033[0;36;40mldap_modify: Type or value exists (20),添加到A组失败 \033[0m')
                except sh.ErrorReturnCode_21 as error:
                    # ldap_add: Invalid syntax (21)
                    print(str(error))
        else:
            pass
            with open('/alidata/scripts/ldap/log/users/new_user/new_user_%s' % time.strftime('%Y-%m-%d',
                                                                                             time.localtime()), 'a',
                      encoding='utf-8') as file_handler:
                file_handler.write(
                    '新增失败人员姓名:{},userid:{},useralias:{},departname:{}'.format(self.username, self.userid, self.useralias,
                                                                            self.departName) + '\n')
    def deleteLdapUser(self):
        try:
            ldap_res = sh.grep(
                sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' % self.username),
                'mail').stdout.decode('utf-8')
            sh.ldapdelete('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w',
                          'limikeji', 'uid=%s,ou=manager,dc=limikeji,dc=com' % self.username)
            with open('/alidata/scripts/ldap/log/users/del_user/del_user_%s' % time.strftime('%Y-%m-%d',time.localtime()), 'a',
                      encoding='utf-8') as file_handler:
                file_handler.write(
                    '删除人员姓名:{}'.format(self.username,) + '\n')
        except:
            pass

    def delete_Depart_User(self):
        try:
            ldap_res = sh.cut(sh.cut(sh.cut(sh.grep(sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'cn=%s'%self.departName),'uid'),'-d',' ','-f2'),'-d',',','-f1'),'-d','=','-f2').stdout.decode('utf-8')
            ldap_resList = str(ldap_res).split('\n')[:-1]  #部门所有的人员姓名
            if 'test' in ldap_resList:
                ldap_resList.remove('test')
                # print('删除组%s'%self.departName)
                # 再删除部门中的用户，如果只是删除用户的话，那么部门中仍然可以看到用户，只是用户的dn是不可用的
                for user in ldap_resList:
                    try:
                        ldap_res = sh.grep(sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' % user),
                            'mail').stdout.decode('utf-8')
                        # print(ldap_res)
                    except sh.ErrorReturnCode_1:
                        with open('/tmp/temp_user_delete_attr.ldif', 'w', encoding='utf-8') as file_handler:
                            file_handler.write(ATTR_DELETE_MODIFY.format_map({
                                'depart_name': self.departName,
                                'username': user
                            }))
                        sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w',
                                   'limikeji', '-f', '/tmp/temp_user_delete_attr.ldif')
            else:
                # print('删除组%s' % self.departName)
                # 再删除部门中的用户，如果只是删除用户的话，那么部门中仍然可以看到用户，只是用户的dn是不可用的，显示结果为一个红叉
                for user in ldap_resList:
                    try:
                        ldap_res = sh.grep(
                            sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' % user),
                            'mail').stdout.decode('utf-8')
                        # print(ldap_res)
                    except sh.ErrorReturnCode_1:
                        with open('/tmp/temp_user_delete_attr.ldif', 'w', encoding='utf-8') as file_handler:
                            file_handler.write(ATTR_DELETE_MODIFY.format_map({
                                'depart_name': self.departName,
                                'username': user
                            }))
                        sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w',
                                   'limikeji', '-f', '/tmp/temp_user_delete_attr.ldif')

        except sh.ErrorReturnCode_1:
            pass

