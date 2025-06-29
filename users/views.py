from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.serializers import UserSerializer
from .models import User
from .permissions import IsActiveUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, IsActiveUser]

        return [permission() for permission in self.permission_classes]
