from .models import Post
from rest_framework import status
from .serializers import PostSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def blog_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


