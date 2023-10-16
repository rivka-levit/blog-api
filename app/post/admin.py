from django.contrib import admin

from post.models import Category, Author


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'ordering']
    list_display_links = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
