# Register your models here.

from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect

from .models import CaptchaImage, ImageSlice

class SliceInline(admin.TabularInline):
    model = ImageSlice
    extra = 0

class CaptchaAdmin(admin.ModelAdmin):
    inlines = [SliceInline]


admin.site.register(CaptchaImage, CaptchaAdmin)

