"""
Serializers for Category, Author, Post, Tag objects.
"""

from rest_framework import serializers

from post.models import Category, Author, Post


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category object."""

    class Meta:
        model = Category
        fields = ['name', 'slug', 'ordering']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author object."""

    class Meta:
        model = Author
        fields = ['name', 'slug']


class AuthorDetailSerializer(AuthorSerializer):
    """Serializer for Author object in detail pages."""

    class Meta(AuthorSerializer.Meta):
        fields = ['name', 'slug', 'description']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post object."""
    category = CategorySerializer(required=False)
    author = AuthorSerializer(required=False)

    class Meta:
        model = Post
        fields = ['title', 'slug', 'category', 'author', 'excerpt', 'image',
                  'time_read', 'created_at', 'updated_at']
