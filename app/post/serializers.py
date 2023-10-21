"""
Serializers for Category, Author, Post, Tag objects.
"""

from rest_framework import serializers

from post.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category object."""

    class Meta:
        model = Category
        fields = ['name', 'slug', 'ordering']
