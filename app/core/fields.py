"""
Custom fields for models.
"""

from django.core import checks
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class OrderField(models.PositiveIntegerField):

    description = 'Ordering field with unique value for a particular field.'

    def __init__(self, unique_to=None, *args, **kwargs):
        self.unique_to = unique_to
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_field_attribute(**kwargs)
        ]

    def _check_field_attribute(self, **kwargs):
        """
        Checks 'unique_to' attribute has been passed and matches an existing
        model field.
        """

        if self.unique_to is None:
            return [
                checks.Error('OrderField must define a "unique_to" attribute.')
            ]

        fields = {field.name for field in self.model._meta.get_fields()}

        if self.unique_to not in fields:
            return [
                checks.Error(
                    'Field name passed with "unique_to" attribute does not '
                    'match an existing model field.'
                )
            ]

        return []

    def pre_save(self, model_instance, add):
        """
        Adding order number automatically if not passed.
        """

        if getattr(model_instance, self.attname) is None:

            qs = self.model.objects.all()

            try:
                query = {self.unique_to: getattr(model_instance, self.unique_to)}
                qs.filter(**query)
                last_item = qs.latest(self.attname)
                value = getattr(last_item, self.attname) + 1
            except ObjectDoesNotExist:
                value = 1

            setattr(model_instance, self.attname, value)

        return super().pre_save(model_instance, add)
