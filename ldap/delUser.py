improt sh
with open('shanuser','r') as d:
    listuser = d.read().split(',')[:-1]
def deleteLdapUser(username):
    try:
        ldap_res = sh.grep(
            sh.ldapsearch('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w', 'limikeji', 'uid=%s' %username),
            'mail').stdout.decode('utf-8')
        sh.ldapdelete('-x', '-D', 'cn=root,dc=limikeji,dc=com', '-w',
                      'limikeji', 'uid=%s,ou=manager,dc=limikeji,dc=com' %username)
    except:
        pass

for user in listuser:
    deleteLdapUser(user)
