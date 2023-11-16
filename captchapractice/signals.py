from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import CaptchaImage, ImageSlice, UploadImage

@receiver(post_save, sender=CaptchaImage)
def create_image_slices(sender, instance, created, **kwargs):
    if created:
        file_name = instance.image_name
        no_of_slices = (instance.slice_count)**2
        for i in range(1, no_of_slices+1):
            ImageSlice.objects.create(root_image=instance, slice_name=f"{file_name}_{i}")

# @receiver(post_save, sender= UploadImage)
# def validate_dimensions(sender, instance, created, **kwargs):
#     if instance.height_field != instance.width_field:
#         raise Exception("file dimensions are not 1:1")
 
