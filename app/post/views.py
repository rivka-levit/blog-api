"""
Views for Category, Author, Post APIs.
"""

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.db.models import Q

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
    PostListSerializer,
    TagSerializer,
    PostImageSerializer,
    SectionSerializer,
    CommentSerializer
)

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
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


@extend_schema_view(
    list=extend_schema(
        description='List of posts.',
        parameters=[
            OpenApiParameter(
                name='author',
                description='The slug of the author.',
                type=OpenApiTypes.STR,
                required=False
            ),
            OpenApiParameter(
                name='category',
                description='The slug of the category.',
                type=OpenApiTypes.STR,
                required=False
            ),
            OpenApiParameter(
                name='tags',
                description="Comma separated list of tags' ids.",
                type=OpenApiTypes.STR,
                required=False
            ),
            OpenApiParameter(
                name='search',
                description='The search term.',
                type=OpenApiTypes.STR,
                required=False
            )
        ]
    ),
    create=extend_schema(
        description='Create a new post.'
    ),
    update=extend_schema(
        description='Full update of the post.'
    ),
    partial_update=extend_schema(
        description='Partial update of the post.'
    ),
    destroy=extend_schema(
        description='Delete an existing post.'
    ),
    upload_image=extend_schema(
        description='Upload an image of the post.'
    ),
    update_section=extend_schema(
        description='Update a single section of the post. Required parameters: '
                    'post slug, ordering number of the section.',
    ),
    delete_section=extend_schema(
        description='Delete a single existing section of the post.'
    )
)
class PostViewSet(BaseViewSet):
    """View for Post APIs."""

    queryset = Post.objects.all().select_related(
        'category',
        'author'
    ).prefetch_related(Prefetch('sections'))

    serializer_class = PostSerializer

    def get_serializer_class(self):
        """Return the proper serializer class for a particular request."""

        if self.action == 'list':
            return PostListSerializer
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
        search = self.request.query_params.get('search', None)

        if search is not None:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(sections__sub_title__icontains=search) |
                Q(sections__content__icontains=search)
            ).distinct()

        if tag_ids is not None:
            try:
                ids = list(map(int, tag_ids.split(',')))
            except ValueError:
                ids = list()

            queryset = queryset.filter(tags__id__in=ids).distinct()

        if autor_slug is not None:
            queryset = queryset.filter(author__slug=autor_slug)

        if category_slug is not None:
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


@extend_schema_view(
    list=extend_schema(
        description='List of comments.',
        parameters=[
            OpenApiParameter(
                name='post',
                description='The slug of the post.',
                type=OpenApiTypes.STR,
                required=False
            ),
            OpenApiParameter(
                name='visible',
                description='Whether or not the comment is visible in the post.',
                type=OpenApiTypes.BOOL,
                required=False
            )
        ]
    ),
    create=extend_schema(
        description='Create a new comment.'
    ),
    update=extend_schema(
        description='Full update of the comment.'
    ),
    partial_update=extend_schema(
        description='Partial update of the comment.'
    ),
    destroy=extend_schema(
        description='Delete an existing comment.'
    )
)
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
