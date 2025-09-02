from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Posts
from users.models import Users
from .serializers import PostSerializer
import ipaddress



class PostViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = '/posts/'

# 1. Create user, login and save tokens on cookies.
        self.user = Users.objects.create_user( 
            username='testuser',
            email='test@example.com', 
            password='somepassword123'
        )        
        token = AccessToken.for_user(self.user)
        token['id'] = self.user.id  
        self.client.cookies['access_token'] = str(token)

        self.valid_payload = {
            'title': 'First Post',
            'content': 'My first post'
        }

        self.post1 = Posts.objects.create(
            title='Post 1',
            content='Content 1',
            username=self.user,
            author_ip='192.168.1.1',
            created_dateTime=timezone.now() - timedelta(days=1),
            is_active=True
        ) 

       
    def test_list_posts_not_authenticated(self):
        self.client.cookies['access_token'] = None 
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_posts_authenticated(self): 
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_posts_not_authenticated(self):
        self.client.cookies['access_token'] = None
        response = self.client.post(self.base_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
   

    def test_new_posts_authenticated(self):
        response = self.client.post(self.base_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)    
     

    def test_update_post_owner(self): 
        edit_url = f'{self.base_url}{self.post1.id}/'      
        data = {
            'title': 'Updated Title',
            'content': 'Updated Content'
        }   
        response = self.client.patch(edit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        


      

