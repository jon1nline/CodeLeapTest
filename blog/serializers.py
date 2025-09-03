from rest_framework import serializers

from .models import Posts


class PostSerializer(serializers.ModelSerializer):
    # For GET requests, displays the user's string representation (e.g., name)
    # instead of just their ID. It's automatically read-only.
    username = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Posts
        fields = [
            "id",
            "title",
            "content",
            "author_ip",
            "username",
            "created_dateTime",
        ]

        # These fields will be sent on GET requests but cannot be set or
        # modified by the client.
        read_only_fields = ["id", "author_ip", "username", "created_dateTime"]

        # These validations apply to POST and PUT, but not PATCH
        extra_kwargs = {
            "title": {"required": True, "min_length": 1, "max_length": 100},
            "content": {"required": True, "min_length": 1, "max_length": 5000},
        }
