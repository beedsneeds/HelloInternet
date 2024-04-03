from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from django.conf import settings

from .models import CaptchaImage
from .utils import make_image_slices

import os


# After a save signal is sent, slices up the image and creates ImageSlice models
@receiver(post_save, sender=CaptchaImage)
def create_image_slices(sender, instance, created, **kwargs):

    if created:
        print("we're reaching create img slices")
        # filename = instance.image_name
        # slice_count = instance.slice_count
        # make_image_slices(filename, slice_count, ip_image_path, slice_out_path, instance)
