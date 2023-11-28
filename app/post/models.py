from django.db import models
from django.conf import settings
from django.utils.text import slugify

from core.fields import OrderField
from post.checks import FieldsValidator

import os
import uuid


def post_image_file_path(instance, filename):
    """Generate file path for a new post image."""

    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'images', filename)


class Category(models.Model):
    """Object of the categories in the blog."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    ordering = OrderField(unique_to='user', null=True, blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def clean(self):
        """Check if slug and ordering number is unique for related user."""

        validator = FieldsValidator()
        validator.check_slug(self)
        validator.check_ordering(self)

    def save(self, *args, **kwargs):
        """Auto field creation and validation before saving."""

        if not self.slug:
            self.slug = slugify(self.name)

        self.full_clean()
        return super(Category, self).save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the object."""

        return self.name


class Author(models.Model):
    """Author object."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authors'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=2000, null=True, blank=True)

    def clean(self):
        """Check if slug is unique for related user."""

        validator = FieldsValidator()
        validator.check_slug(self)

    def save(self, *args, **kwargs):
        """Auto field creation and validation before saving."""

        if not self.slug:
            self.slug = slugify(self.name)

        self.full_clean()
        return super(Author, self).save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the object."""

        return self.name


class Post(models.Model):
    """Post object."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    excerpt = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(
        upload_to=post_image_file_path,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        to=Author,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True
    )
    time_read = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Check if slug is unique for related user."""

        validator = FieldsValidator()
        validator.check_slug(self)

    def save(self, *args, **kwargs):
        """Auto field creation and validation before saving."""

        if not self.slug:
            self.slug = slugify(self.title)

        self.full_clean()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the object."""

        return self.title


class Section(models.Model):
    """Text sections of the post object."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    ordering = OrderField(unique_to='post', null=True, blank=True)
    sub_title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()

    class Meta:
        ordering = ['ordering', 'pk']

    def clean(self):
        """Check if ordering number is unique for the particula post."""

        validator = FieldsValidator()
        validator.check_ordering(self)

    def save(self, *args, **kwargs):
        """Auto field creation and validation before saving."""

        self.full_clean()
        return super(Section, self).save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the object."""

        sub_title = self.sub_title if self.sub_title else ''

        return f'{self.ordering}. {sub_title}'


class Tag(models.Model):
    """Tag object."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags'
    )
    post = models.ManyToManyField(to=Post, related_name='tags')
    name = models.CharField(max_length=100)

    def __str__(self):
        """Return a string representation of the object."""

        return self.name


class Comment(models.Model):
    """Comments for posts."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=150, null=True, blank=True)
    message = models.TextField(max_length=1500)

    def __str__(self):
        """Return a string representation of the object."""

        return f'Comment number {self.id}.'
