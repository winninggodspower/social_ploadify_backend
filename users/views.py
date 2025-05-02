from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterUserSerializer

# Create your views here.

class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
