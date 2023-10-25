"""
Serializers for Category, Author, Post, Tag objects.
"""

from django.shortcuts import get_object_or_404

from rest_framework import serializers

from post.models import Category, Author, Post, Section


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


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section object."""

    class Meta(AuthorSerializer.Meta):
        model = Section
        fields = ['id', 'sub_title', 'ordering', 'content']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post object."""

    category = CategorySerializer(required=False)
    author = AuthorSerializer(required=False)
    sections = SectionSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'slug', 'category', 'author', 'excerpt', 'image',
                  'time_read', 'created_at', 'updated_at', 'sections']

    def create(self, validated_data):
        """Create a post."""

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)
        sections = validated_data.pop('sections', [])

        post = Post.objects.create(**validated_data)

        if category_data:
            category = get_object_or_404(Category, **category_data)
            post.category = category

        if author_data:
            author = get_object_or_404(Author, **author_data)
            post.author = author

        if sections:
            for section in sections:
                Section.objects.create(
                    user=self.context['request'].user,
                    post=post,
                    **section
                )

        post.save()

        return post

    def update(self, instance, validated_data):
        """Update a post."""

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category_data:
            category = get_object_or_404(Category, **category_data)
            instance.category = category

        if author_data:
            author = get_object_or_404(Author, **author_data)
            instance.author = author

        instance.save()

        return instance
