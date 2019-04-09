from django_python3_ldap import ldap
import ldap3
from django_python3_ldap.conf import settings
from django.contrib.auth.models import Group

import logging
logger = logging.getLogger('django')

class SyncDjangoLDAP():
    """
    Class for synchronizing LDAP groups to Django and Django db to LDAP.
    """
    def __init__(self, user):
        """
        Creates the LDAP connection.
        """
        # create connection
        username = f'uid={user.username},ou=people,dc=gis,dc=lab'
        password= user.password

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

        self._connection = c

    def change_user(self, obj, form):
        logger.info('change_user function')
        if 'first_name' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                    {'givenName': [(ldap3.MODIFY_REPLACE, [f'{obj.first_name}'])]})
            logger.info(f'Account {obj.username} updated with first name {obj.first_name}')
        if 'last_name' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                                    {'sn': [(ldap3.MODIFY_REPLACE, [f'{obj.last_name}'])]})
            logger.info(f'Account {obj.username} updated with surname {obj.last_name}')
        if 'email' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                {'mail': [(ldap3.MODIFY_REPLACE, [f'{obj.email}'])]})
            logger.info(f'Account {obj.username} updated with mail {obj.email}')
        if 'description' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                {'description': [(ldap3.MODIFY_REPLACE, [f'{obj.description}'])]})
            logger.info(f'Account {obj.username} updated with description {obj.description}')


    def save_user(self, obj, form):
        logger.info('save_user function')
