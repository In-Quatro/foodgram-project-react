import csv
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from api.serializers import (
    CustomUserReadSerializer,
    CustomUserSerializer,
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    SetPasswordSerializer,
    RecipeSerializer,
    RecipeReadSerializer,
)
from rest_framework.response import Response
from users.models import User, Subscription
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart,
    RecipeIngredient,
)


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для Пользователя."""
    queryset = User.objects.all()

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
        """Изменение пароля."""
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
        subscribeed_by = User.objects.filter(subscribeed_by__user=request.user)
        serializer = SubscriptionSerializer(
            subscribeed_by,
            many=True,
            context={'request': request})
        return Response(serializer.data)

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


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для Рецептов."""
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def interaction_recipe(self, request, pk, model):
        """Вспомогательный метод
        для добавления Рецепта в Избранное и Корзину."""
        if model.__name__ == 'Favorite':
            message_1, message_2 = 'Избранном', 'Избранного'
        elif model.__name__ == 'ShoppingCart':
            message_1, message_2 = 'Корзине', 'Корзины'
        recipe = get_object_or_404(Recipe, id=pk)
        presence_object = model.objects.filter(
            recipe=recipe,
            user=request.user).exists()
        if request.method == 'POST':
            if presence_object:
                return Response(
                    {'errors': f'Данный рецепт уже в {message_1}!'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            model.objects.create(user=request.user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not presence_object:
                return Response(
                    {'errors': f'Рецепт нельзя удалить из {message_2}, '
                               f'поскольку его нет в {message_1}.'},
                    status=status.HTTP_400_BAD_REQUEST)
            delete_recipe = get_object_or_404(
                model,
                user=request.user,
                recipe=recipe
            )
            delete_recipe.delete()
            return Response(
                {'detail': f'Рецепт удален из {message_2}.'},
                status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        return self.interaction_recipe(request, pk, Favorite)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        return self.interaction_recipe(request, pk, ShoppingCart)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        ingredients_obj = RecipeIngredient.objects.filter(
            recipe__recipes_in_cart__user=request.user
        ).values('ingredient'
                 ).annotate(total_amount=Sum('amount')
                            ).values_list('ingredient__name',
                                          'total_amount',
                                          'ingredient__measurement_unit')
        data = [ingredients for ingredients in ingredients_obj]

        filename = 'recipe.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
            writer.writerows(data)

        response = HttpResponse(open(filename, 'rb'), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для Тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для Ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
