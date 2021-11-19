from django.urls import include, path
from rest_framework.routers import DefaultRouter

from foodgram.views import IngredientsViewSet, RecipeViewSet, TagsViewSet

app_name = 'foodgram'

router = DefaultRouter()
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
