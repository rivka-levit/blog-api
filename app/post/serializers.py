"""
Serializers for Category, Author, Post, Tag objects.
"""

from django.shortcuts import get_object_or_404

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

    def create(self, validated_data):
        """Create a post."""

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)

        post = Post.objects.create(**validated_data)

        if category_data:
            category = get_object_or_404(Category, **category_data)
            post.category = category

        if author_data:
            author = get_object_or_404(Author, **author_data)
            post.author = author

        post.save()

        return post
