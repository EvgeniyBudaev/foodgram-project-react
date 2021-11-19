from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from foodgram.models import (Cart, Favorite, Ingredient, Recipe,
                             RecipeIngredient, Tag)
from users.models import Follow
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиент."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Тег."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели РецептИнгредиент."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredient.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт."""
    image = Base64ImageField(max_length=None, use_url=True)
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'tags',)

    def get_is_favorited(self, obj):
        """Проверка добавлен ли рецепт в избранное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Favorite.objects.filter(user=request.user.id,
                                           recipe=obj.id).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()

    def validate_tags(self, data):
        """Валидация поля Тэг."""
        if not data:
            raise serializers.ValidationError(
                'Вы не добавили ни одного Тэга!')
        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                'Тэг не может повторяться')
        return data

    def validate_ingredients(self, data):
        """Валидация поля Ингредиент."""
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингредиент для рецепта'})
        unique_ingredients = set()
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=ingredient_item['id'])
            if ingredient in unique_ingredients:
                raise serializers.ValidationError('Ингредиенты должны '
                                                  'быть уникальными')
            unique_ingredients.add(ingredient['id'])
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create_or_update_tags_and_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(Tag.objects.filter(
            id__in=tags))
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount'])

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.create_or_update_tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.initial_data.get('ingredients')
        instance.image = validated_data.get('image', instance.image)
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_or_update_tags_and_ingredients(instance, tags, ingredients)
        super().update(instance, validated_data)
        return instance


class CropRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор выдает только необходимые поля."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Избранное."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')
        extra_kwargs = {'user': {'write_only': True},
                        'recipe': {'write_only': True}}

    def validate(self, data):
        """Валидация при добавлении рецепта в избранное."""
        if Favorite.objects.filter(user=data['user'],
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError('Рецепт уже есть в избранном!')
        return data


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор модели Список Покупок."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Cart
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')
        extra_kwargs = {'user': {'write_only': True},
                        'recipe': {'write_only': True}}

    def validate(self, data):
        """Валидация при добавлении рецепта в список покупок."""
        if Cart.objects.filter(user=data['user'],
                               recipe=data['recipe']).exists():
            raise serializers.ValidationError('Рецепт уже есть в списке'
                                              ' покупок!')
        return data


class FollowSerializer(serializers.ModelSerializer):
    """Подписки."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return CropRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
