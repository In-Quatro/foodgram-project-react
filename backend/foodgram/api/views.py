from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from api.serializers import (
    UserReadSerializer,
    UserSerializer,
    RecipeIngredientSerializer,
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    SetPasswordSerializer,
)
from rest_framework.response import Response
from users.models import User, Subscription
from recipes.models import (
    RecipeIngredient,
    Recipe,
    Tag,
    Ingredient,
)


class ReadOnlyMixins(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,   # убрать поле после проверки
                 viewsets.GenericViewSet):
    """Миксин для [GET] метода."""
    pass


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для Пользователя."""
    queryset = User.objects.all()
    # serializer_class = UserGetSerializer

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return UserReadSerializer
        return UserSerializer

    @action(methods=['get'],
            detail=False,)
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=False,)
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для Рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для Тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', 'post']


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для Ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get', 'post']


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer