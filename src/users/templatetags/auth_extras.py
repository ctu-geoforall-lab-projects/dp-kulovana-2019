from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Returns whether user belongs to a given group or not
    """
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False

    return group in user.groups.all()

@register.filter(name='list_groups')
def list_groups(request):
    """
    Returns list of existing groups in Django
    """
    return Group.objects.all()
