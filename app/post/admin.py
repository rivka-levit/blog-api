from django.contrib import admin

from post.models import Category, Author, Post, Section, Tag, Comment


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


class SectionInline(admin.TabularInline):
    model = Section
    fields = ['ordering', 'sub_title', 'content', 'user', 'post']
    extra = 1


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'name', 'message', 'date_created',
                    'date_updated', 'is_visible']
    readonly_fields = ['date_created', 'date_updated']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SectionInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
