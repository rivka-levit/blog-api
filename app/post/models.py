from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from core.fields import OrderField


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

        qs = Category.objects.filter(
            user=self.user, slug=self.slug
        ).exclude(pk=self.pk)

        if qs:
            raise ValidationError(
                'The slug must be unique for this particular user.'
            )

        qs = Category.objects.filter(
            user=self.user, ordering=self.ordering
        ).exclude(pk=self.pk)

        if qs:
            raise ValidationError(
                'The ordering number of a category must be unique for this '
                'particular user.'
            )

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

        qs = Author.objects.filter(
            user=self.user, slug=self.slug
        ).exclude(pk=self.pk)

        if qs:
            raise ValidationError(
                'The slug must be unique for this particular user.'
            )

    def save(self, *args, **kwargs):
        """Auto field creation and validation before saving."""

        if not self.slug:
            self.slug = slugify(self.name)

        self.full_clean()
        return super(Author, self).save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the object."""

        return self.name
