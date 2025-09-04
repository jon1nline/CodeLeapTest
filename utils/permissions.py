from rest_framework import permissions

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # leitura liberada
        if request.method in permissions.SAFE_METHODS:
            return True

        # 👉 Se não estiver autenticado, nem chega aqui
        if not request.user or not request.user.is_authenticated:
            return False
        
        return obj.username == request.user
