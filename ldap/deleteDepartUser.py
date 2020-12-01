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

def delete_Depart_User(departName):
    try:
        ldap_res = sh.cut(sh.cut(sh.cut(sh.grep(sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'cn=%s'%departName),'uid'),'-d',' ','-f2'),'-d',',','-f1'),'-d','=','-f2').stdout.decode('utf-8')
        ldap_resList = str(ldap_res).split('\n')[:-1]  #部门所有的人员姓名
        if 'test' in ldap_resList:
            ldap_resList.remove('test')
            print('删除组%s'%departName)
            # 再删除部门中的用户，如果只是删除用户的话，那么部门中仍然可以看到用户，只是用户的dn是不可用的，显示结果为一个红叉
            for user in ldap_resList:
                try:
                    ldap_res = sh.grep(sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' % user),
                        'mail').stdout.decode('utf-8')
                    print(ldap_res)
                except sh.ErrorReturnCode_1:
                    with open('/tmp/temp_user_delete_attr.ldif', 'w', encoding='utf-8') as file_handler:
                        file_handler.write(ATTR_DELETE_MODIFY.format_map({
                            'depart_name': departName,
                            'username': user
                        }))
                    sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w',
                               'limikeji', '-f', '/tmp/temp_user_delete_attr.ldif')
        else:
            print('删除组%s' % departName)
            for user in ldap_resList:

                try:
                    ldap_res = sh.grep(
                        sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' % user),
                        'mail').stdout.decode('utf-8')
                    print(ldap_res)
                except sh.ErrorReturnCode_1:
                    with open('/tmp/temp_user_delete_attr.ldif', 'w', encoding='utf-8') as file_handler:
                        file_handler.write(ATTR_DELETE_MODIFY.format_map({
                            'depart_name': departName,
                            'username': user
                        }))
                    sh.ldapadd('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w',
                               'limikeji', '-f', '/tmp/temp_user_delete_attr.ldif')

    except sh.ErrorReturnCode_1:
        pass

with open('/alidata/scripts/syncdingldap/ldap/zu','r') as depart:
    listDepart = depart.read().split('\n')[:-1]
for zu in listDepart:
    delete_Depart_User(zu)