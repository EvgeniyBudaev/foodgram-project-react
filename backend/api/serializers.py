from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from foodgram.models import (Cart, Favorite, Ingredient, RecipeIngredient,
                             Recipe, Tag)
from users.models import Follow
from users.serializers import CustomUserSerializer


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор модели Подписка."""
    id = serializers.ReadOnlyField(source='author.id')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'first_name', 'last_name', 'username', 'email',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()


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
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=RecipeIngredient.objects.all(),
        #         fields=['ingredient', 'recipe']
        #     )
        # ]


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт, GET запрос."""

    ingredients = RecipeIngredientSerializer(source='recipe_ingredient',
                                             many=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        """
        Проверка добавлен ли рецепт в избранное.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Favorite.objects.filter(user=request.user.id,
                                           recipe=obj.id).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        """
        Проверка добавлен ли рецепт в список покупок.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Cart.objects.filter(user=request.user.id,
                                       recipe=obj.id).exists()
        return queryset


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Рецепт, POST запрос."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(source='recipe_ingredient',
                                             many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    image = Base64ImageField()
    name = serializers.CharField(validators=[UniqueValidator(
        queryset=Recipe.objects.all(),
        message='Такой рецепт уже существует!')])

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate_cooking_time(self, data):
        """
        Валидация поля время приготовления.
        """
        if data < 1:
            raise serializers.ValidationError(
                'Время приготовления указано не верно!')
        return data

    def validate_tags(self, data):
        """
        Валидация поля Тэг.
        """
        if not data:
            raise serializers.ValidationError(
                'Вы не добавили ни одного Тэга!')
        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                'Тэг не может повторяться')
        return data

    def validate_ingredients(self, data):
        """
        Валидация поля Ингредиент.
        """
        ingredients = self.initial_data.get('ingredients')
        unique_ingredients = set()
        for ingredient in ingredients:
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    'Слишком малое количество ингредиента!')
            if ingredient['id'] in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться')
            unique_ingredients.add(ingredient['id'])
        return data

    def create_recipe_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient_id=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        validated_data.pop('recipe_ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        validated_data.pop('recipe_ingredient')
        ingredients = self.initial_data.get('ingredients')
        # instance.name = validated_data['name']
        # instance.text = validated_data['text']
        # instance.cooking_time = validated_data['cooking_time']
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_recipe_ingredient(ingredients, instance)
        instance = super().validated_data
        instance.save()
        return instance


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
