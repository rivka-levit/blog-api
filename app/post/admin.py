from django.contrib import admin

from post.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'ordering']
    list_display_links = ['name', 'slug']
