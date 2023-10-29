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

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)
        sections = validated_data.pop('sections', [])
        tags = validated_data.pop('tags', [])

        post = Post.objects.create(**validated_data)

        self._assign_parameters(post, category_data, author_data,
                                sections, tags)
        return post

    def update(self, instance, validated_data):
        """Update a post."""

        category_data = validated_data.pop('category', None)
        author_data = validated_data.pop('author', None)
        sections = validated_data.pop('sections', [])
        tags = validated_data.pop('tags', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        self._assign_parameters(instance, category_data, author_data,
                                sections, tags)
        return instance

    def _assign_parameters(self,
                           post: Post,
                           category_data: dict,
                           author_data: dict,
                           sections: list[dict],
                           tags: list[dict]) -> None:
        """Assign parameters to the post"""

        if category_data:
            post.category = self._get_category(category_data)

        if author_data:
            post.author = self._get_author(author_data)

        if sections:
            self._create_post_sections(sections, post)

        if tags:
            self._assign_tags(tags, post)

        post.save()

    def _assign_tags(self, tags: list[dict], post: Post) -> None:
        """Get or create tags and assign them to the post."""

        auth_user = self.context['request'].user

        if post.tags:
            post.tags.clear()

        for tag_data in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag_data
            )
            post.tags.add(tag_obj)

        post.save()

    def _get_category(self, category_data: dict) -> Category:
        """Get and return a category from the database."""

        auth_user = self.context['request'].user

        return get_object_or_404(Category, user=auth_user, **category_data)

    def _get_author(self, author_data: dict) -> Author:
        """Get and return an author from the database."""

        auth_user = self.context['request'].user

        return get_object_or_404(Author, user=auth_user, **author_data)

    def _create_post_sections(self, sections: list[dict], post: Post) -> None:
        """Create sections for a particular post"""

        auth_user = self.context['request'].user

        old_sections = post.sections.all()
        if old_sections.exists():
            for section in old_sections:
                section.delete()

        for section_data in sections:
            Section.objects.create(
                user=auth_user,
                post=post,
                **section_data
            )


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to posts."""

    class Meta:
        model = Post
        fields = ['slug', 'image']
        read_only_fields = ['slug']
        extra_kwargs = {'image': {'required': 'True'}}
