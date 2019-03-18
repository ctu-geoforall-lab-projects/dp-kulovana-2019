from django_python3_ldap.ldap import connection
import ldap3
from django_python3_ldap.conf import settings
from django_python3_ldap.utils import format_search_filter

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

    # get attributes of gislabadmins
    group = 'gislabadmins'
    CUSTOM_SEARCH_FILTER = f'(&(ObjectClass=posixGroup)(cn={group})(memberUid={user.username}))'
    SEARCH_BASE_GROUPS = "ou=groups,dc=gis,dc=lab"
    search_res = c.search(
            search_base = SEARCH_BASE_GROUPS,
            search_filter = CUSTOM_SEARCH_FILTER,
            attributes=ldap3.ALL_ATTRIBUTES,
    )

    # check whether is user is superuser
    if search_res:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        logger.info(f'User {user.username} is in {group}')
    else:
        logger.info(f'User {user.username} is not in {group}')

    # All done!
    return
