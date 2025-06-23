from rest_framework import serializers
from .models import Posts

class PostsSerializer(serializers.ModelSerializer):
    
    username = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Posts
        # Adicione 'username' à lista de campos
        fields = ['id', 'title', 'content', 'author_ip', 'likes', 'username']
        extra_kwargs = {
            'title': {'required': True, 'max_length': 100, 'min_length': 1},
            'content': {'required': True, 'max_length': 5000, 'min_length': 1},
            'author_ip': {'required': True, 'max_length': 20, 'min_length': 1},
            'likes': {'required': False, 'allow_null': True}
        }

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = '__all__'  # Include all fields
        read_only_fields = ['id', 'username', 'created_time', 'likes','author_ip']
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': True},
        }

class PostDelete(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = '__all__'  # Include all fields
               