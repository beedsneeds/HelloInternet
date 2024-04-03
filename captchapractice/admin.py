# Register your models here.

from django.contrib import admin

# from django.http.request import HttpRequest
# from django.http.response import HttpResponse
# from django.shortcuts import redirect

from .models import CaptchaImage, ImageSlice
from .forms import ImageSliceForm


# Even though you can change details in the admin interface, the slice creation process does
# not run again to handle model editing. So unless your changes to the model are either difficulty_level
# or element_presence, it's a better idea to delete this model and create a fresh one
class SliceInline(admin.StackedInline):
    model = ImageSlice
    form = ImageSliceForm
    extra = 0


class CaptchaAdmin(admin.ModelAdmin):
    inlines = [SliceInline]


admin.site.register(CaptchaImage, CaptchaAdmin)
