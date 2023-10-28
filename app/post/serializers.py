"""
Serializers for Category, Author, Post, Tag objects.
"""

from django.shortcuts import get_object_or_404

from rest_framework import serializers

from post.models import Category, Author, Post, Section, Tag


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


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag object."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section object."""

    class Meta(AuthorSerializer.Meta):
        model = Section
        fields = ['id', 'sub_title', 'ordering', 'content']
        read_only_fields = ['id']
        ordering = ['ordering']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post object."""

    category = CategorySerializer(required=False)
    author = AuthorSerializer(required=False)
    sections = SectionSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'slug', 'category', 'author', 'excerpt', 'image',
                  'time_read', 'created_at', 'updated_at', 'sections', 'tags']

    def create(self, validated_data):
        """Create a post."""

        auth_user = self.context['request'].user

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)
        sections = validated_data.pop('sections', [])
        tags = validated_data.pop('tags', [])

        post = Post.objects.create(**validated_data)

        if category_data:
            category = get_object_or_404(
                Category,
                user=auth_user,
                **category_data
            )
            post.category = category

        if author_data:
            author = get_object_or_404(Author, user=auth_user, **author_data)
            post.author = author

        if sections:
            for section in sections:
                Section.objects.create(
                    user=auth_user,
                    post=post,
                    **section
                )

        if tags:
            for tag in tags:
                tag_obj = self._get_or_create_tag(tag)
                post.tags.add(tag_obj)

        post.save()

        return post

    def update(self, instance, validated_data):
        """Update a post."""

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)
        sections = validated_data.pop('sections', [])
        tags = validated_data.pop('tags', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category_data:
            category = get_object_or_404(Category, **category_data)
            instance.category = category

        if author_data:
            author = get_object_or_404(Author, **author_data)
            instance.author = author

        if sections:
            for section in instance.sections.all():
                section.delete()

            for section in sections:
                Section.objects.create(
                    user=self.context['request'].user,
                    post=instance,
                    **section
                )

        if tags:
            instance.tags.clear()

            for tag in tags:
                tag_obj = self._get_or_create_tag(tag)
                instance.tags.add(tag_obj)

        instance.save()

        return instance

    def _get_or_create_tag(self, tag_data):
        """Retrieve or create and return a tag object."""

        auth_user = self.context['request'].user

        tag_obj, created = Tag.objects.get_or_create(
            user=auth_user,
            **tag_data
        )

        return tag_obj
