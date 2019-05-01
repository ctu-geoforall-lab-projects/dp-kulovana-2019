from django_python3_ldap import ldap
import ldap3
from django_python3_ldap.conf import settings
from django.contrib.auth.models import Group
import logging
logger = logging.getLogger('django')

class SyncDjangoLDAP():
    """Synchronize changes and new models from Django db into LDAP."""

    def __init__(self):
        """Creates the LDAP connection."""

        username = f'uid=django_admin,ou=People,dc=gis,dc=lab'
        password = 'django2019'

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
        """Change user attributes in LDAP according to Django changes."""

        logger.info('SyncDjangoLDAP change_user function')

        if 'first_name' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                    {'givenName': [(ldap3.MODIFY_REPLACE, [f'{obj.first_name}'])]})
            logger.info(f'Account {obj.username} updated with first name {obj.first_name}')

        if 'last_name' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                                    {'sn': [(ldap3.MODIFY_REPLACE, [f'{obj.last_name}'])]})
            logger.info(f'Account {obj.username} updated with surname {obj.last_name}')

        if 'first_name' or 'last_name' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                    {'cn': [(ldap3.MODIFY_REPLACE, [f'{obj.first_name} {obj.last_name}'])]})
            logger.info(f'Account {obj.username} updated with cn {obj.first_name} {obj.last_name}')

        if 'email' in form.changed_data:
            self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                {'mail': [(ldap3.MODIFY_REPLACE, [f'{obj.email}'])]})
            logger.info(f'Account {obj.username} updated with mail {obj.email}')

        if 'description' in form.changed_data:
            if not obj.description:
                self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                    {'description': [(ldap3.MODIFY_DELETE, [])]})
            else:
                self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
                    {'description': [(ldap3.MODIFY_REPLACE, [f'{obj.description}'])]})
            logger.info(f'Account {obj.username} updated with description {obj.description}')

        if 'groups' in form.changed_data:

            # get all existing Django groups
            groups_django = Group.objects.all()

            for one_group_django in groups_django:

                # check if user is in Django group
                django_group = obj.groups.filter(name=f'{one_group_django}').exists()

                # check if user is in the same LDAP group
                ldap_group = self._ldap_group_membership(obj, one_group_django)

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

    def change_password(self, obj, new_password):
        """Change user password in LDAP according to Django changes."""

        logger.info('SyncDjangoLDAP change_password function')

        # change password in LDAP
        self._connection.modify(f'uid={obj.username},ou=People,dc=gis,dc=lab',
            {'userPassword': [(ldap3.MODIFY_REPLACE, [new_password])]})
        logger.info(f'Account {obj.username} updated with password {new_password}')

    def save_user(self, obj, password):
        """Add new user into LDAP."""

        logger.info('SyncDjangoLDAP save_user function')

        # add new user into LDAP
        self._connection.add(f'uid={obj.username},ou=People,dc=gis,dc=lab', attributes={
            'objectClass': ['inetOrgPerson', 'posixAccount', 'shadowAccount'],
            'uidNumber': 3005,
            'gidNumber': 3001,
            'homeDirectory': f'/mnt/home/{obj.username}',
            'loginShell': '/bin/bash',
            'cn': f'{obj.first_name} {obj.last_name}',
            'sn': f'{obj.last_name}',
            'givenName': f'{obj.first_name}',
            'mail': f'{obj.email}',
            'userPassword': password
            }
        )
        logger.info(f'Successfully added user {obj.username} to LDAP')

    def delete_user(self, obj):
        """Delete user from LDAP."""

        logger.info('SyncDjangoLDAP delete_user function')

        # remove all user relations from LDAP
        groups_django = Group.objects.all()
        for one_group_django in groups_django:
            if self._ldap_group_membership(obj, one_group_django):
                self._connection.modify(f'cn={one_group_django},ou=Groups,dc=gis,dc=lab',
                    {'memberUid': [(ldap3.MODIFY_DELETE, [f'{obj.username}'])]})

        # delete user from LDAP
        self._connection.delete(f'uid={obj.username},ou=People,dc=gis,dc=lab')
        logger.info(f'Successfully deleted user {obj.username} from LDAP')

    def save_group(self, obj, form):
        """Add new group into LDAP."""

        logger.info('SyncDjangoLDAP save_group function')

        # add new group into LDAP
        self._connection.add(f'cn={obj.name},ou=Groups,dc=gis,dc=lab', attributes={
            'objectClass': ['posixGroup', ],
            'cn': f'{obj.name}',
            'gidNumber': 3105
             }
        )
        logger.info(f'Successfully added group {obj.name} to LDAP')

    def delete_group(self, obj):
        """Delete group from LDAP."""

        logger.info('SyncDjangoLDAP delete_group function')

        # get LDAP group
        SEARCH_BASE_GROUPS = "ou=groups,dc=gis,dc=lab"
        CUSTOM_SEARCH_FILTER = f'(&(ObjectClass=posixGroup)(cn={obj.name}))'
        self._connection.search(
            search_base = SEARCH_BASE_GROUPS,
            search_filter = CUSTOM_SEARCH_FILTER,
            attributes=ldap3.ALL_ATTRIBUTES,
        )
        ldap_group = self._connection.entries

        # get users belonging to a selected group and delete them
        for entry in ldap_group:
            try:
                for user in entry.memberUid:
                    self._connection.modify(f'cn={obj.name},ou=Groups,dc=gis,dc=lab',
                        {'memberUid': [(ldap3.MODIFY_DELETE, [f'{user}'])]})
            except:
                pass

        # delete group from LDAP
        self._connection.delete(f'cn={obj.name},ou=Groups,dc=gis,dc=lab')
        logger.info(f'Successfully deleted group {obj.name} from LDAP')

    def _ldap_group_membership(self, obj, group):
        """Returns whether user belongs to a selected group in LDAP.."""

        # check if user is in the LDAP group
        SEARCH_BASE_GROUPS = "ou=groups,dc=gis,dc=lab"
        CUSTOM_SEARCH_FILTER = f'(&(ObjectClass=posixGroup)(cn={group})(memberUid={obj.username}))'
        ldap_group = self._connection.search(
            search_base = SEARCH_BASE_GROUPS,
            search_filter = CUSTOM_SEARCH_FILTER,
            attributes=ldap3.ALL_ATTRIBUTES,
        )
        return ldap_group
