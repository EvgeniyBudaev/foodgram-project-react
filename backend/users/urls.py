from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser import views

from users.views import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', views.TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', views.TokenDestroyView.as_view(),
         name='logout'),
]
