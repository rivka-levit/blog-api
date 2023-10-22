"""
URL mappings for Category, Author, Post APIs.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from post.views import CategoryViewSet, AuthorViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('', include(router.urls))
]
