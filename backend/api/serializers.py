from rest_framework import serializers

from users.models import Follow


class FollowSerializer(serializers.ModelSerializer):
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
