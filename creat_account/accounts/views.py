from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

from .models import *

class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            data={'message': f'Bye {request.user.username}!'},
            status=status.HTTP_204_NO_CONTENT
        )


class UserRegistration(APIView):
    def post(self,request):
        User_serializer=UserSerializer(data=request.data)
        if User_serializer.is_valid():
            User_serializer.save()
            return Response({'message': 'User added successfully!'})
        

