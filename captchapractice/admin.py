# Register your models here.

from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect

from .models import CaptchaImage, ImageSlice, ImageSliceForm


class SliceInline(admin.StackedInline):
    model = ImageSlice
    form = ImageSliceForm
    extra = 0


class CaptchaAdmin(admin.ModelAdmin):
    inlines = [SliceInline]


admin.site.register(CaptchaImage, CaptchaAdmin)
