from django.contrib import admin
from .models import Post

admin.site.site_header = "Lost And Found MMU Admin"
admin.site.site_title = "Lost And Found MMU Admin"
admin.site.index_title = "Lost And Found MMU Admin"

class PostAdmin(admin.ModelAdmin):

    list_display = ('title', 'publish_date', 'updated_at', 'author', 'status')
    search_fields = ('title',)
    list_filter = ('status',)
    list_per_pages = 20
    actions = ('set_post_to_published',)

    def set_post_to_published (self, request, queryset):
        count = queryset.update(status='published')
        self.message_user(request, '{}Posts have been published successfully.'.format(count))
    set_post_to_published.short_description = 'Mark selecteds as published'

admin.site.register(Post, PostAdmin)

