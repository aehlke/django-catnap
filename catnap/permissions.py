# Partially adapted from django.db.models.query_utils.Q
# and django-rest-framework's permissions.py

from django.utils import tree
from django.core.exceptions import PermissionDenied

from exceptions import NotAuthenticated


READ_ONLY_METHODS = ['GET', 'HEAD', 'OPTIONS']
_AND = 'AND'
_OR = 'OR'


def _evaluate_node(node, request, view):
    '''
    Returns a 2-tuple of (has_permission, permission_exception)
    '''
    evaluated_permission = None
    permission_exception = None

    children = node.children if len(node.children) > 0 else [node]

    for child in children:
        if len(child.children) > 0:
            child_permission, permission_exception = _evaluate_node(child, request, view)
        else:
            try:
                child.verify_permission(request, view)
                child_permission = True
            except (PermissionDenied, NotAuthenticated) as e:
                permission_exception = e
                child_permission = False

        if node.connector == _OR and child_permission:
            return (True, permission_exception)
        elif node.connector == _AND and not child_permission:
            return (False, permission_exception)

        if evaluated_permission is None:
            evaluated_permission = child_permission
        elif node.connector == _AND:
            evaluated_permission = evaluated_permission and child_permission
        elif node.connector == _OR:
            evaluated_permission = evaluated_permission or child_permission

    if node.negated:
        evaluated_permission = not evaluated_permission

    return (evaluated_permission, permission_exception)


class PermissionsMixin(object):
    '''
    Mixin to use for catnap REST views.

    You must override the `permissions` property with whichever
    authentication methods you want, either a single one or several
    joined by bitwise operators (&, |, ~).
    '''
    permissions = None

    def dispatch(self, request, *args, **kwargs):
        if self.permissions is None:
            raise NotImplementedError("Must override the permissions property.")

        has_permission, permission_exception = _evaluate_node(self.permissions, request, self)

        if not has_permission:
            raise permission_exception

        return super(PermissionsMixin, self).dispatch(request, *args, **kwargs)


class BasePermission(tree.Node):
    default = _AND

    def _combine(self, other, conn):
        if not isinstance(other, BasePermission):
            raise TypeError(other)

        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, _OR)

    def __and__(self, other):
        return self._combine(other, _AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, _AND)
        obj.negate()
        return obj

    def verify_permission(self, request, view):
        '''
        Insufficient permission will raise an exception.
        '''
        raise NotImplementedError("Must override the verify_permission method.")

    def has_permission(self, request, view):
        try:
            self.verify_permission(request, view)
            return True
        except (PermissionDenied, NotAuthenticated):
            return False


class AllowAny(BasePermission):
    def verify_permission(self, request, view):
        pass


class IsAuthenticated(BasePermission):
    def verify_permission(self, request, view):
        if not request.user.is_authenticated():
            raise NotAuthenticated()
