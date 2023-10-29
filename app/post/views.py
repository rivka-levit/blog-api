"""
Views for Category, Author, Post APIs.
"""

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.permissions import AccessOwnerOnly

from post.models import Category, Author, Post, Tag
from post.serializers import (
    CategorySerializer,
    AuthorSerializer,
    AuthorDetailSerializer,
    PostSerializer,
    TagSerializer,
    PostImageSerializer
)


class BaseViewSet(viewsets.ModelViewSet):
    """Base view set for APIs."""

    permission_classes = [IsAuthenticated, AccessOwnerOnly]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'slug'

    def get_queryset(self):
        """Filter the queryset by user."""

        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assign the new category to the authenticated user."""

        serializer.save(user=self.request.user)


class CategoryViewSet(BaseViewSet):
    """View for Category APIs."""

    queryset = Category.objects.all().order_by('ordering')
    serializer_class = CategorySerializer


class AuthorViewSet(BaseViewSet):
    """View for Author APIs."""

    queryset = Author.objects.all()
    serializer_class = AuthorDetailSerializer

    def get_serializer_class(self):
        """Return the serializer for a particular action."""

        if self.action == 'list':
            return AuthorSerializer

        return self.serializer_class


class PostViewSet(BaseViewSet):
    """View for Post APIs."""

    queryset = Post.objects.all().select_related(
        'category',
        'author'
    ).prefetch_related(Prefetch('sections'))

    serializer_class = PostSerializer

    def get_serializer_class(self):
        """Return the proper serializer class for a particular request."""

        if self.action == 'upload_image':
            return PostImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, slug=None):
        """Uploading image to a post."""

        post = get_object_or_404(Post, slug=slug)
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(BaseViewSet):
    """View for Tag APIs."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'
