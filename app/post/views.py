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

from post.models import Category, Author, Post, Tag, Section, Comment
from post.serializers import (
    CategorySerializer,
    AuthorSerializer,
    AuthorDetailSerializer,
    PostSerializer,
    TagSerializer,
    PostImageSerializer,
    SectionSerializer,
    CommentSerializer
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
        if self.action == 'update_section':
            return SectionSerializer

        return self.serializer_class

    def get_queryset(self):
        """Filter and return the queryset."""

        queryset = super().get_queryset()

        autor_slug = self.request.query_params.get('author', None)
        category_slug = self.request.query_params.get('category', None)
        tag_ids = self.request.query_params.get('tags', None)

        if tag_ids:
            ids = list(map(int, tag_ids.split(',')))
            queryset = queryset.filter(tags__id__in=ids).distinct()

        if autor_slug:
            queryset = queryset.filter(author__slug=autor_slug)

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, slug=None):
        """Uploading image to a post."""

        post = get_object_or_404(Post, slug=slug)
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PATCH'],
            detail=True,
            url_path=r'update-section/(?P<sect_ord>\d+)')
    def update_section(self, request, slug=None, sect_ord=None):
        """Update a single section of a particular post."""

        post = get_object_or_404(Post, slug=slug)
        section = get_object_or_404(Section, post=post, ordering=sect_ord)

        for key, value in request.data.items():
            setattr(section, key, value)

        section.save()

        return Response(SectionSerializer(section).data, status=status.HTTP_200_OK)

    @action(methods=['DELETE'],
            detail=True,
            url_path=r'delete-section/(?P<sect_ord>\d+)')
    def delete_section(self, request, slug=None, sect_ord=None):
        """Remove a single section of a particular post."""

        post = get_object_or_404(Post, slug=slug)
        section = get_object_or_404(Section, post=post, ordering=sect_ord)

        section.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(BaseViewSet):
    """View for Tag APIs."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'


class CommentViewSet(BaseViewSet):
    """View for Comment APIs."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """Filter the queryset."""

        qs = super().get_queryset()

        post_slug = self.request.query_params.get('post', None)
        visible = self.request.query_params.get('visible', None)

        if post_slug:
            post = get_object_or_404(Post, slug=post_slug)
            qs = qs.filter(post=post)

        if visible == 'false':
            qs = qs.filter(is_visible=False)
        elif visible == 'true':
            qs = qs.filter(is_visible=True)

        return qs
