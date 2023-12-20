from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import CaptchaImage, ImageSlice
from .utils import validate_dimensions, make_slices

import os 


# I've hardcoded .jpg in a lot of places in utils. Find a way to fix it (see if it breaks anything)
# will it work with gifs, I wonder

# checks if the image is in 1:1 ratio, if so, slices up the image and creates ImageSlice models
@receiver(post_save, sender=CaptchaImage)
def validate_and_create_slices(sender, instance, created, **kwargs):
    
    up_dir = settings.MEDIA_ROOT
    #  make these two less long by using some static root setting
    up_image_out = os.path.join(settings.BASE_DIR, 'captchapractice', 'static', 'captchapractice', 'images', 'prompt candidates')
    slice_out = os.path.join(settings.BASE_DIR, 'captchapractice', 'static', 'captchapractice', 'images', 'prompts')
    
    if created:
        if not validate_dimensions(instance, up_dir, up_image_out):
            raise ValidationError("Image does not have 1:1 dimensions. Press back and retry with appropriate dimensions")
        else:
            # else just call a function that does the clice creation process

            filename = instance.image_name
            slice_count = instance.slice_count
            make_slices(filename, slice_count, up_image_out, slice_out)
            # create_slice_objects(filename, slice_count, instance)
            
            no_of_slice_objects = (slice_count)**2
            for i in range(1, no_of_slice_objects+1):
                ImageSlice.objects.create(root_image=instance, slice_name=f"{filename}_{i}")

