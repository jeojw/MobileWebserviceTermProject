from rest_framework import viewsets

class BlogImages(viewsets.ModelViewSet):
    queryset = Post
    serializer_class = Post