from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()

from api.pagination import LimitPageNumberPagination
from api.serializers import FollowSerializer
from users.models import Follow


class CustomUserViewSet(UserViewSet):
    """
    Общий вьюсет для всех эндпоинтов /users/.
    """
    pagination_class = LimitPageNumberPagination

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """
        Отображение страницы с подписками авторизованного пользователя.
        """
        user = request.user
        context = {'request': request}
        queryset = Follow.objects.filter(follower=user)
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = FollowSerializer(
                pages,
                many=True,
                context=context
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            queryset,
            many=True,
            context=context,
        )
        return Response(serializer.data)
