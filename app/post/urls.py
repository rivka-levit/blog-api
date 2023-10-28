"""
URL mappings for Category, Author, Post APIs.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from post.views import CategoryViewSet, AuthorViewSet, PostViewSet, TagViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('authors', AuthorViewSet, basename='author')
router.register('posts', PostViewSet, basename='post')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls))
]
