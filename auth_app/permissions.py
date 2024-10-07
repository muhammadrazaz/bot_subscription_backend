from rest_framework.permissions import BasePermission
class IsInGroupsOrSuperUser(BasePermission):
    def __init__(self, allowed_groups=None):
        if allowed_groups is None:
            allowed_groups = []
        self.allowed_groups = allowed_groups

    def __call__(self):
        return self

    def has_permission(self, request, view):
        # return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.groups.filter(name__in=self.allowed_groups).exists() or request.user.is_superuser:
            return True
        return False
    

def IsInGroupsOrSuperUserFactory(allowed_groups=[]):
    # return True
    return IsInGroupsOrSuperUser(allowed_groups=allowed_groups)