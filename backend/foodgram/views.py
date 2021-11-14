from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram.models import (Cart, Favorite, Ingredient, RecipeIngredient,
                             Recipe, Tag)
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, TagSerializer,
                             RecipeSerializer, RecipeGetSerializer)


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Вьюсет модели Ингредиент."""
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagsViewSet(ReadOnlyModelViewSet):
    """Вьюсет модели Тег."""
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    """Вьюсет модели Рецепт."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Метод создания - удаления обьекта подписки."""
        recipe = get_object_or_404(Recipe, id=pk).id
        user = self.request.user.id
        exist = Favorite.objects.filter(user=user, recipe=recipe).exists()

        if request.method == 'GET':
            data = {'user': user, 'recipe': recipe}
            context = {'request': request}
            serializer = FavoriteSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and exist:
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Этого рецепта нет в избранном!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Метод создания - удаления обьекта в списке покупок."""
        recipe = get_object_or_404(Recipe, id=pk).id
        user = self.request.user.id
        exist = Cart.objects.filter(user=user, recipe=recipe).exists()

        if request.method == 'GET':
            data = {'user': user, 'recipe': recipe}
            context = {'request': request}
            serializer = CartSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and exist:
            Cart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Этого рецепта нет в списке покупок!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def download_shopping_cart(self, request):
        """
        Скачивание списка покупок.
        """
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user)

        ingredients_count = {}
        for recipe_ingredient in ingredients:
            if recipe_ingredient.ingredient in ingredients_count:
                ingredients_count[recipe_ingredient.ingredient] += (
                    recipe_ingredient.amount)
            else:
                ingredients_count[recipe_ingredient.ingredient] = (
                    recipe_ingredient.amount)

        result = ''
        for ingredient in ingredients_count:
            weight = 0
            weight += ingredients_count[ingredient]
            result += (f'{ingredient.name} - {str(weight)} '
                       f'{ingredient.measurement_unit}.')

        download = 'buy_list.txt'
        response = HttpResponse(
            result, content_type="text/plain,charset=utf8")
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(download)
        )
        return response
