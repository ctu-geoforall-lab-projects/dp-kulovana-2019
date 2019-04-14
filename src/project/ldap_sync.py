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
        if 'groups' in form.changed_data:
            groups_django = Group.objects.all()
            for one_group_django in groups_django:
                # check if user is in Django group
                django_group = obj.groups.filter(name=f'{one_group_django}').exists()
                # check if user is in the same LDAP group
                ldap_group = _ldap_group_membeship(obj, one_group_django)
                # user in Django and not in LDAP
                if django_group and not ldap_group:
                    self._connection.modify(f'cn={one_group_django},ou=Groups,dc=gis,dc=lab',
                        {'memberUid': [(ldap3.MODIFY_ADD, [f'{obj.username}'])]})
                    logger.info(f'Account {obj.username} was added to group {one_group_django}')

                # user not in Django and in LDAP
                elif not django_group and ldap_group:
                    self._connection.modify(f'cn={one_group_django},ou=Groups,dc=gis,dc=lab',
                        {'memberUid': [(ldap3.MODIFY_DELETE, [f'{obj.username}'])]})
                    logger.info(f'Account {obj.username} was deleted from group {one_group_django}')

                # add superuser status respectively to gislabadmins status
                if one_group_django.name == 'gislabadmins':
                    obj.is_staff = django_group
                    obj.is_superuser = django_group
                    obj.save()
                    if django_group:
                        logger.info(f'User {obj.username} is a superuser')


    def save_user(self, obj, form):
        logger.info('save_user function')
        self._connection.add(f'uid={obj.username},ou=People,dc=gis,dc=lab', attributes={
            'objectClass': ['inetOrgPerson', 'posixAccount', 'shadowAccount'],
            'uidNumber': 3005,
            'gidNumber': 3001,
            'homeDirectory': f'/mnt/home/{obj.username}',
            'loginShell': '/bin/bash',
            'cn': '{obj.first_name} + {obj.last_name}',
            'sn': '{obj.last_name}',
            'givenName': '{obj.first_name}',
            'mail': '{obj.email}',
            'userPassword': obj.password
            }
        )
        logger.info(f'Successfully added user {obj.username} to LDAP')

    def delete_user(self, obj):
        # remove all user relations from LDAP
        groups_django = Group.objects.all()
        for one_group_django in groups_django:
            if self._ldap_group_membership(obj, one_group_django):
                self._connection.modify(f'cn={one_group_django},ou=Groups,dc=gis,dc=lab',
                    {'memberUid': [(ldap3.MODIFY_DELETE, [f'{obj.username}'])]})
        # delete user from LDAP
        self._connection.delete(f'uid={obj.username},ou=People,dc=gis,dc=lab')
        logger.info(f'Successfully deleted user {obj.username} from LDAP')

    def _ldap_group_membership(self, obj, group):
        # check if user is in the LDAP group
        SEARCH_BASE_GROUPS = "ou=groups,dc=gis,dc=lab"
        CUSTOM_SEARCH_FILTER = f'(&(ObjectClass=posixGroup)(cn={group})(memberUid={obj.username}))'
        ldap_group = self._connection.search(
            search_base = SEARCH_BASE_GROUPS,
            search_filter = CUSTOM_SEARCH_FILTER,
            attributes=ldap3.ALL_ATTRIBUTES,
        )
        return ldap_group
