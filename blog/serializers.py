from rest_framework import serializers

from .models import Posts


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(source="username", read_only=True)
    created_at = serializers.DateTimeField(source="created_dateTime", read_only=True)

    class Meta:
        model = Posts
        fields = [
            "id",
            "title",
            "content",
            "author",
            "created_at",
        ]

        read_only_fields = ["id", "author", "created_at"]

        extra_kwargs = {
            "title": {"required": True, "min_length": 1, "max_length": 100},
            "content": {"required": True, "min_length": 1, "max_length": 5000},
        }
