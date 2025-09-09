from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    publish_date = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('draft','Draft'), ('published','Published')],
        default='draft'
    )
    image = models.ImageField(upload_to="posts/", null=True, blank=True)

    def __str__(self):
        return self.title



