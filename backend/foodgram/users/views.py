from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    CustomUserReadSerializer,
    CustomUserSerializer,
    SetPasswordSerializer,
    SubscriptionSerializer,
)
from api.paginations import CustomPagination

from users.models import User, Subscription


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для Пользователя."""
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserReadSerializer
        return CustomUserSerializer

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Просмотр своего профиля."""
        serializer = CustomUserReadSerializer(request.user)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """Изменение своего пароля."""
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Просмотр своих подписок."""
        subscribed_by = User.objects.filter(subscribed_by__user=request.user)
        pages = self.paginate_queryset(subscribed_by)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        """Подписка на пользователя."""
        author = get_object_or_404(User, id=pk)
        if author == request.user:
            return Response(
                {'errors': f'Запрещено подписываться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        subscribe = Subscription.objects.filter(
            author=author,
            user=request.user).exists()
        if request.method == 'POST':
            if subscribe:
                return Response(
                    {'errors': f'Вы уже подписаны на "{author}"'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscribe:
                return Response(
                    {'errors': f'Нельзя удалить из подписок "{author}",'
                               f'поскольку вы еще не подписаны на него!'},
                    status=status.HTTP_400_BAD_REQUEST)
            delete_subscribe = get_object_or_404(
                Subscription,
                user=request.user,
                author=author
            )
            delete_subscribe.delete()
            return Response(
                {'detail': f'Вы отписались от "{author}".'},
                status=status.HTTP_204_NO_CONTENT)
