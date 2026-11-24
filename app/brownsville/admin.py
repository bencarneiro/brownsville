from django.contrib import admin
from .models import Agent, Listing, ListingPhoto


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "mls_id", "phone", "email", "license_number")
    search_fields = ("name", "mls_id", "email", "phone")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("mls_number", "street_number", "street_name", "city", "property_type", "list_price", "agent", "priority")
    list_filter = ("property_type", "city", "agent")
    search_fields = ("mls_number", "street_name", "subdivision", "city")
    inlines = [ListingPhotoInline]


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "slug", "path", "is_highlight")
    search_fields = ("listing__mls_number", "slug", "path")