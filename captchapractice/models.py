from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from django.forms import ModelForm


# Create your models here.

'''
    Configured a 'post-save' signal:
        When an instance is created, a signal is sent (signals.py) 
        to automatically create (slice_count**2) image slices.
            Naming system in line with image slicer (make_slices) fn
        To modify, only fiddle with signals.py.
        To configure for the first time or remove, look in apps.py
            (probably the most involved method compared to overriding the 
            'save' model method or creating a custom manager class)

    Used signal again for validating image dimensions. 
    What I tried:
        overriding save() [method in ModelManager class]
        overriding clean() [form validation that's run during save in admin page]
        writing custom FileUploadHandler class in place of ImageField
        validating ImageField with custom validator from within ImageField args
        performing a pre-save signal based approach instead of post-save
        admin.ModelAdmin: def response_add() - auto-chaining the model instance
            creation process with creation of other models

    What I didn't try:
        Just writing custom views outside of django-admin, for my specific needs 

'''


class CaptchaImage(models.Model):
    image = models.ImageField(upload_to="admin uploads/", null=True)  # MEDIA_ROOT/admin uploads/
    image_name = models.CharField(max_length=10, unique=True, help_text='Enter an abbreviated image name (max length 10 characters). Do not include an extension')
    prompt_text = models.CharField(max_length=200, help_text='The prompt the user sees. Eg: "Select all the cars in the image" ') 

    SLICE_CHOICES = [
        (3, "3x3 Grid"),
        (4, "4x4 Grid"),
        (5, "5x5 Grid"),
    ]
    slice_count = models.IntegerField(
        choices=SLICE_CHOICES,
        default=3,
    )
    
    DIFFICULTY = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard"),
    ]
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY,
        default=1
    )

    def __str__(self):
        return self.prompt_text
    
    def get_absolute_url(self):
        return reverse('captchapractice:selection', args=[str(self.id)])
    
    def correct_choices(self, image_id):
        result = []
        correct_choices = ImageSlice.objects.filter(root_image=image_id).filter(element_presence=1).values("slice_name")
            # returns an iterable QuerySet object consisting of single element dictionaries for each ImageSlice object
        correct_choices = list(correct_choices)
        
        for item in correct_choices:
            for key in item:
                result.append(item[key])
        
        return result

    def get_img_slice_list(self, image_id):
        result = ImageSlice.objects.filter(root_image=image_id)
        return result

    # class Meta:
    #     ordering = ['-difficulty_level']
# using order_by query instead from within views


class ImageSlice(models.Model):
    root_image = models.ForeignKey(CaptchaImage, on_delete=models.CASCADE)
    slice_name = models.CharField(max_length=13)
    element_presence = models.BooleanField(default=False)
    # rename element presense to object presence

    def __str__(self):
        return self.slice_name

class ImageSliceForm(ModelForm):
    class Meta:
        model = ImageSlice
        fields = ["element_presence"]


class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def solved_history(self, user):
        history = UserResponses.objects.filter(user=user)
        return history


class UserResponses(models.Model):
    root_image = models.ForeignKey(CaptchaImage, on_delete=models.SET_NULL, null=True, blank=True)
    # response_json = models.JSONField(null=True) 
    response_json = models.TextField(null=True, max_length=800)   
        # max length dependant on how large the image grid is + length of imageslice names
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

