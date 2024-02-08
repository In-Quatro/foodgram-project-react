from rest_framework import permissions


class IsAuthorPermission(permissions.BasePermission):
    """Изменение объектов доступно только для Автора и Администратора."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_superuser)
