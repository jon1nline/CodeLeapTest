from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from users.models import Users 
import jwt

class CustomJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Authorization header must be in the format "Bearer <token>"')
        if len(parts) == 1:
            raise exceptions.AuthenticationFailed('Token not found')
        if len(parts) > 2:
            raise exceptions.AuthenticationFailed('Authorization header must be "Bearer <token>"')

        token = parts[1]

        try:
            # Decodifica o token usando a sua SECRET_KEY
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # Verifica se o token tem o campo 'id' e se é do tipo 'access'
            if 'id' not in payload or payload.get('token_type') != 'access':
                raise exceptions.AuthenticationFailed('Invalid token payload')
            
            user_id = payload['id']
            user = Users.objects.get(id=user_id)
            
            # Retorna o usuário e o token para o DRF
            return (user, token)
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Invalid token signature')
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Token validation failed: {e}')