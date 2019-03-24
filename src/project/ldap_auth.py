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

    groups_ldap = c.entries

    # list of LDAP group names
    groups_ldap_cn = []
    for one_group_ldap in groups_ldap:
        groups_ldap_cn.append(one_group_ldap.cn.value)
    logger.info(f'List of group names (CN) in LDAP: {groups_ldap_cn}')

    # test if all Django groups are in LDAP
    groups_django = Group.objects.all()
    logger.info(f'List of django groups before comparison: {Group.objects.all()}')
    for one_group_django in groups_django:
        if one_group_django.name not in groups_ldap_cn:
            Group.objects.get(name=one_group_django).delete()
            logger.info(f'Group {one_group_django} was deleted from Django')
    logger.info(f'List of django groups after comparison: {Group.objects.all()}')

    # iterate through groups
    for group in groups_ldap:

        # get a group object if already exists or create a new group
        new_group, created = Group.objects.get_or_create(name=group.cn)

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
            logger.info(f'User {user.username} is in {group.cn}')
        else:
            user.groups.remove(new_group)
            logger.info(f'User {user.username} is not in {group.cn}')

        # if user part of gislabadmins -> add superuser status
        if group.cn == "gislabadmins":
                user.is_staff = search_res
                user.is_superuser = search_res
                user.save()
                if search_res:
                    logger.info(f'User {user.username} is a superuser')

    # All done!
    return
