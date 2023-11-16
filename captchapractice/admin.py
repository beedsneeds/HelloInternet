# Register your models here.

from django.contrib import admin

from .models import CaptchaImage, ImageSlice, UploadImage

class SliceInline(admin.TabularInline):
    model = ImageSlice
    extra = 0

class CaptchaAdmin(admin.ModelAdmin):
    inlines = [SliceInline]


admin.site.register(CaptchaImage, CaptchaAdmin)

admin.site.register(UploadImage)
