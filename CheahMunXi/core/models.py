from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=[("lost", "Lost"), ("found", "Found")])
    category = models.CharField(max_length=50, null=True, blank=True)
    image = models.CharField(max_length=100, null=True, blank=True)  # or ImageField if needed
    date_posted = models.DateTimeField(default=now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "post"   # 🔑 must match your existing table name
        managed = False     # ✅ don't let Django try to migrate/modify it

    def __str__(self):
        return self.title
