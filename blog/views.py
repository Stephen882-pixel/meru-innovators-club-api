from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from .models import Blog
from .serializers import BlogSerializer


class BlogView(APIView):
    allowed_methods = ['GET', 'POST', 'PATCH', 'DELETE']
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="List blogs created by the authenticated user",
        operation_description="Retrieve all blogs owned by the authenticated user. "
                              "Optional `search` query filters blogs by title or content.",
        tags=["Blogs"],
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search blogs by title or blog_text",
                type=openapi.TYPE_STRING,
                required=False,
                example="innovation"
            )
        ],
        responses={
            200: openapi.Response(
                description="Blogs fetched successfully",
                examples={
                    "application/json": {
                        "data": [
                            {
                                "uid": "abc123",
                                "title": "My first blog",
                                "blog_text": "This is an example blog.",
                                "user": 1,
                                "created_at": "2025-08-19T12:00:00Z"
                            }
                        ],
                        "message": "blog fetched successfully"
                    }
                }
            ),
            400: "Something went wrong"
        }
    )
    def get(self, request):
        try:
            blogs = Blog.objects.filter(user=request.user)

            if request.GET.get('search'):
                search = request.GET.get('search')
                blogs = blogs.filter(Q(title__icontains=search) | Q(blog_text__icontains=search))

            serializer = BlogSerializer(blogs, many=True)

            return Response({
                'data': serializer.data,
                'message': 'blog fetched successfully',
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'data': {},
                'message': 'Something went wrong',
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Create a new blog",
        operation_description="Create a blog owned by the authenticated user.",
        tags=["Blogs"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "blog_text"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="My new blog"),
                "blog_text": openapi.Schema(type=openapi.TYPE_STRING, example="This is the content of the blog."),
            },
        ),
        responses={
            201: openapi.Response(
                description="Blog created successfully",
                examples={
                    "application/json": {
                        "data": {
                            "uid": "xyz456",
                            "title": "My new blog",
                            "blog_text": "This is the content of the blog.",
                            "user": 1,
                            "created_at": "2025-08-19T13:00:00Z"
                        },
                        "message": "Blog created successfully"
                    }
                }
            ),
            400: "Validation failed"
        }
    )
    def post(self, request):
        try:
            data = request.data.copy()
            data['user'] = request.user.id

            serializer = BlogSerializer(data=data)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Validation failed'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                'data': serializer.data,
                'message': 'Blog created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'data': {},
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update an existing blog",
        operation_description="Partially update a blog owned by the authenticated user. Requires `uid` in request body.",
        tags=["Blogs"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["uid"],
            properties={
                "uid": openapi.Schema(type=openapi.TYPE_STRING, example="abc123"),
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Updated blog title"),
                "blog_text": openapi.Schema(type=openapi.TYPE_STRING, example="Updated blog content."),
            },
        ),
        responses={
            200: openapi.Response(
                description="Blog updated successfully",
                examples={
                    "application/json": {
                        "data": {
                            "uid": "abc123",
                            "title": "Updated blog title",
                            "blog_text": "Updated blog content.",
                            "user": 1,
                            "created_at": "2025-08-19T12:00:00Z",
                            "updated_at": "2025-08-19T13:30:00Z"
                        },
                        "message": "blog updated successfully"
                    }
                }
            ),
            400: "Invalid blog uid / validation error",
            403: "You are not authorized to do this"
        }
    )
    def patch(self, request):
        try:
            data = request.data
            if not data.get('uid'):
                return Response({
                    'data': {},
                    'message': 'blog uid is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            blog = Blog.objects.filter(uid=data.get('uid'))
            if not blog.exists():
                return Response({
                    'data': {},
                    'message': 'invalid blog uid'
                }, status=status.HTTP_400_BAD_REQUEST)

            blog_obj = blog.first()
            if request.user != blog_obj.user:
                return Response({
                    'data': {},
                    'message': 'you are not authorized to do this'
                }, status=status.HTTP_403_FORBIDDEN)

            serializer = BlogSerializer(blog_obj, data=data, partial=True)
            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                'data': serializer.data,
                'message': 'blog updated successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'data': {},
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete a blog",
        operation_description="Delete a blog owned by the authenticated user. Requires `uid` in request body.",
        tags=["Blogs"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["uid"],
            properties={
                "uid": openapi.Schema(type=openapi.TYPE_STRING, example="abc123"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Blog deleted successfully",
                examples={
                    "application/json": {
                        "data": {},
                        "message": "blog deleted successfully"
                    }
                }
            ),
            400: "Invalid blog uid",
            403: "You are not authorized to do this"
        }
    )
    def delete(self, request):
        try:
            data = request.data
            blog = Blog.objects.filter(uid=data.get('uid'))
            if not blog.exists():
                return Response({
                    'data': {},
                    'message': 'invalid blog uid'
                }, status=status.HTTP_400_BAD_REQUEST)
            if request.user != blog[0].user:
                return Response({
                    'data': {},
                    'message': 'you are not authorized to do this'
                }, status=status.HTTP_400_BAD_REQUEST)

            blog[0].delete()
            return Response({
                'data': {},
                'message': 'blog deleted successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'data': {},
                'message': 'something went wrong'
            }, status=status.HTTP_400_BAD_REQUEST)
