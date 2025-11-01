from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post
from .serializers import PostSerializer

class BlogImages(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-published_date')
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser)