"""Permissions DRF et helpers RBAC."""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import User


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", None) == User.Role.ADMIN)


class IsBusinessRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", None) == User.Role.BUSINESS)


class IsExpertRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", None) == User.Role.EXPERT)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
