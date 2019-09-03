from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from . import models


class RepositoryInline(admin.TabularInline):
    model = models.Repository


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "username", "path", "size", "used")
    list_filter = ("host",)
    search_fields = ("name",)
    inlines = (RepositoryInline,)
    exclude = ("size", "used")


@admin.register(models.Repository)
class RepositoryAdmin(GuardedModelAdmin):
    list_filter = ("server",)
    search_fields = ("name",)
    readonly_fields = ("secret",)
    exclude = ("updated", "raw", "compressed", "deduplicated")
