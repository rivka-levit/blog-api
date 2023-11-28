from django.core.exceptions import ValidationError


class FieldsValidator:
    """Validate slug and ordering fields."""

    @staticmethod
    def check_slug(instance):
        """Check if slug is unique for this user."""

        qs = instance.__class__.objects.filter(
            user=instance.user, slug=instance.slug
        ).exclude(pk=instance.pk)

        if qs:
            raise ValidationError(
                'The slug must be unique for this particular user.'
            )

    @staticmethod
    def check_ordering(instance):
        """Check if ordering number is unique for this user."""

        qs = instance.__class__.objects.filter(
            user=instance.user, ordering=instance.ordering
        ).exclude(pk=instance.pk)

        if qs:
            raise ValidationError(
                'The ordering number of a category must be unique for this '
                'particular user.'
            )
