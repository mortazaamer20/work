from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_perm(context, resource, action):
    user = context.get("request", None)
    if user:
        user = user.user
    if not user or not user.is_authenticated:
        return False
    return user.has_resource_perm(resource, action)


@register.filter
def can_view(user, resource):
    return user.has_resource_perm(resource, "view")


@register.filter
def can_add(user, resource):
    return user.has_resource_perm(resource, "add")


@register.filter
def can_edit(user, resource):
    return user.has_resource_perm(resource, "edit")


@register.filter
def can_delete(user, resource):
    return user.has_resource_perm(resource, "delete")
