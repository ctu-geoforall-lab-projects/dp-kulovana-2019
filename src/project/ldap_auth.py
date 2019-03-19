from django_python3_ldap.ldap import connection
import ldap3
from django_python3_ldap.conf import settings
from django.contrib.auth.models import Group

import logging
logger = logging.getLogger('django')

def custom_sync_user_relations(user, ldap_attributes):

    # create connection
    username = None
    password= None
    auto_bind = ldap3.AUTO_BIND_TLS_BEFORE_BIND

    c = ldap3.Connection(
            ldap3.Server(
                settings.LDAP_AUTH_URL,
                allowed_referral_hosts=[("*", True)],
                get_info=ldap3.NONE,
                connect_timeout=settings.LDAP_AUTH_CONNECT_TIMEOUT,
            ),
            user=username,
            password=password,
            auto_bind=auto_bind,
            raise_exceptions=True,
            receive_timeout=settings.LDAP_AUTH_RECEIVE_TIMEOUT,
    )

    # get list of existing groups
    SEARCH_BASE_GROUPS = "ou=groups,dc=gis,dc=lab"
    search_group = c.search(
            search_base = SEARCH_BASE_GROUPS,
            search_filter = '(ObjectClass=posixGroup)',
            attributes = ldap3.ALL_ATTRIBUTES,
    )

    group_list = c.entries

    # iterate through groups
    for group in group_list:

        # get a group object if already exists or create a new group
        new_group, created = Group.objects.get_or_create(name=group.cn)
        logger.info(f'{group.cn} was created')

        # check whether is user in a selected group
        CUSTOM_SEARCH_FILTER = f'(&(ObjectClass=posixGroup)(cn={group.cn})(memberUid={user.username}))'
        search_res = c.search(
                search_base = SEARCH_BASE_GROUPS,
                search_filter = CUSTOM_SEARCH_FILTER,
                attributes=ldap3.ALL_ATTRIBUTES,
        )

        # add user to a selected group
        if search_res:
            user.groups.add(new_group)
            # if user part of gislabadmins -> add superuser status
            if group.cn == "gislabadmins":
                user.is_staff = True
                user.is_superuser = True
                user.save()
            logger.info(f'User {user.username} is in {group.cn}')
        else:
            logger.info(f'User {user.username} is not in {group.cn}')

    # All done!
    return
