#!/bin/bash
cd /alidata/scripts/syncdingldap/
/usr/local/python3/bin/python3 /alidata/scripts/syncdingldap/core.py > /alidata/scripts/ldap/log/sync_log/sync_$(date +%F-%T).log
