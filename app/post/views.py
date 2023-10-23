"""
Views for Category, Author, Post APIs.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.permissions import AccessOwnerOnly

from post.models import Category, Author, Post
from post.serializers import (
    CategorySerializer,
    AuthorSerializer,
    AuthorDetailSerializer,
    PostSerializer
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

    queryset = Category.objects.all()
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

    queryset = Post.objects.all()
    serializer_class = PostSerializer
