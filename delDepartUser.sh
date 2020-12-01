#!/bin/bash
cd /alidata/scripts/syncdingldap/ldap
/usr/local/python3/bin/python3 /alidata/scripts/syncdingldap/ldap/deleteDepartUser.py > /alidata/scripts/ldap/log/sync_log/delDepartUser_$(date +%F-%T).log
