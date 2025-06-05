from rest_framework import serializers
from .models import Posts

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = '__all__'

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = '__all__'  # Include all fields
        read_only_fields = ['id', 'username', 'created_time']
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': True},
        }