from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ImageSlice


class NewCaptchaForm_Upload(forms.Form):
    image = forms.ImageField(
        help_text="Only accepts images with 1:1 dimensions",
    )
    filename = forms.CharField(
        max_length=10,
        help_text="Enter an abbreviated image name. Do not include any extension like .jpg",
    )


class NewCaptchaForm_Details(forms.Form):
    # I tried using the ModelForm but the form.is_valid check fails no matter what I tried:
    # 1) Set self.fields["image_name"].initial = filename & self.fields["image_name"].disabled = True
    # Error isn't descriptive <bound method BaseForm.non_field_errors of <NewCaptchaForm_Details
    # bound=False, valid=False, fields=(image_name;slice_count;difficulty_level;selected_object)>>
    # Check note https://docs.djangoproject.com/en/5.0/topics/forms/modelforms/#selecting-the-fields-to-use
    # Additionally, prompt_text ought to be: f"Select the {selected_object} in the image" not "selected_obj"
    # 2) Set save(commit=False). Didn't work because I can't use form.cleaned_data
    # -- SO, I've just used base Form class and manually handle the object creation logic in the views
    # Even then, passing an argument into a form took a lot of tinkering and trial and error
    # Error handling in Forms isn't very descriptive

    SLICE_CHOICES = [
        (3, "3x3 Grid"),
        (4, "4x4 Grid"),
        (5, "5x5 Grid"),
    ]
    slice_count = forms.ChoiceField(
        choices=SLICE_CHOICES,
        help_text="Determines the grid layout of the created captcha.",
    )

    DIFFICULTY = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard"),
    ]
    difficulty_level = forms.ChoiceField(
        choices=DIFFICULTY,
        help_text="Plays a role in determining the order of captchas presented during a challenge set",
    )

    selected_object = forms.ChoiceField(
        choices=[("a", "b"), ("c", "d")]
    )  # These are overwritten

    def __init__(self, *args, **kwargs):
        # Call standard init with the additional kwarg 'detected_classes'
        detected_classes = kwargs.pop("detected_classes", None)
        super(NewCaptchaForm_Details, self).__init__(*args, **kwargs)
        # Extend init
        # Override the selected_object FormField
        if detected_classes:
            self.fields["selected_object"] = forms.ChoiceField(choices=detected_classes)


class ImageSliceForm(forms.ModelForm):
    class Meta:
        model = ImageSlice
        fields = ["element_presence"]


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
