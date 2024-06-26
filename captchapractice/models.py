from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from random import sample
from django.core import serializers


# delete when porting to new DB
# game moidel & image field of captchaimage & rename element presense to object presence


"""
    Configured a 'post-save' signal:
        When an instance is created, a signal is sent (signals.py) 
        to automatically create (slice_count**2) image slices.
            Naming system in line with image slicer (make_image_slices) fn
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
        Trying to incorporate async JS in admin

"""


class CaptchaImage(models.Model):
    image = models.ImageField(
        upload_to="admin uploads/",
        null=True,
        help_text="Only accepts images with 1:1 dimensions",
    )  # MEDIA_ROOT/admin uploads/
    # can be deleted entirely
    image_name = models.CharField(
        max_length=10,
        unique=True,
    )
    prompt_text = models.CharField(
        max_length=200,
        help_text='The prompt the user sees. Eg: "Select all the cars in the image" ',
    )

    # If these dicitionaries change, change the same in forms. Duplication of code explained there
    SLICE_CHOICES = [
        (3, "3x3 Grid"),
        (4, "4x4 Grid"),
        (5, "5x5 Grid"),
    ]
    slice_count = models.IntegerField(choices=SLICE_CHOICES, default=3)

    DIFFICULTY = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard"),
    ]
    difficulty_level = models.IntegerField(choices=DIFFICULTY, default=1)

    def __str__(self):
        return self.prompt_text

    def get_absolute_url(self):
        return reverse("captchapractice:selection", args=[str(self.id)])
 
    def correct_choices(self, image_id):
        result = list(
            ImageSlice.objects.filter(root_image=image_id)
            .filter(element_presence=1)
            .values_list("slice_name", flat=True)
        )
        return result

    def get_img_slice_list(self, image_id=None, image_name=None):
        """Arguments: pass either the pk (image_id) or the unique image_name """
        if image_id:
            result = ImageSlice.objects.filter(root_image=image_id)
        elif image_name:
            result = ImageSlice.objects.filter(root_image__image_name=image_name)
        return result
    
    # separate function because the serializer source tag requires only self args
    # When refactoring to make this purely back end, replace all the function calls 
    # of the above
    def api_get_img_slice_list_as_json(self):
        intermediate = ImageSlice.objects.filter(root_image=self.id).values("slice_name", "element_presence")
        # result = serializers.serialize('json', intermediate)
        return intermediate


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

    class Meta:
        ordering = ["slice_name"]


class Game(models.Model):
    # This class doesn't need to exist. The methods could be transplanted somewhere else.
    # It's a placeholder for future functionality
    # delete when porting to new DB
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


class UserResponses(models.Model):
    root_image = models.ForeignKey(
        CaptchaImage, on_delete=models.SET_NULL, null=True, blank=True
    )
    response_json = models.TextField(null=True, max_length=800)
    # Max length dependent on how large the image grid is + length of imageslice suffixes
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # percieved_inaccuracy = models.BooleanField(default=False)

    def evaluate_response(correct_choices, selected_choices):
        selected = set(selected_choices)
        correct = set(correct_choices)
        evaluation = dict()

        # Members that are 'correct' in the traditional sense (they occur in both sets) i.e. set intersection
        evaluation["true_positives"] = correct & selected
        # Members that were wrong. That is, those that were not 'correct' but were selected nonetheless
        evaluation["false_postives"] = selected - correct
        # Members that were 'correct' but weren't selected
        evaluation["false_negatives"] = correct - selected

        # Testing for set equality (both sets have the same elements)
        if selected == correct:
            evaluation["text"] = "You are correct!"
        elif len(evaluation["false_negatives"]) > 0:
            evaluation["text"] = "Uh-oh! You missed an image or two."
        else:
            evaluation["text"] = "Oops, you got it wrong!"

        return evaluation


# This is a class-less method
def get_captcha_order(user):
    solved_history = set(
        UserResponses.objects.filter(user=user).values_list("root_image", flat=True)
    )
    unsolved_captcha_list = CaptchaImage.objects.exclude(id__in=solved_history)
    # unsolved_captcha_list = CaptchaImage.objects.all()
    # For testing the bottom line is picked. For production, use the top line

    # It creates a randomized list of captcha primary keys. Total length of quiz is 4:
    # The first will always be easy difficulty. 2nd medium.
    # 3rd & 4th will be hard (because hard ones are interesting
    captcha_quiz_order = []
    for i in range(1, 4):
        filtered_by_difficulty = list(
            unsolved_captcha_list.filter(difficulty_level=i).values_list(
                "pk", flat=True
            )
        )

        # Skips adding a captcha to the quiz list if there are none of that difficulty type left unanswered
        # Reluctant to add 'magic numbers' 1, 2, 3 here. Will fix this hardcoded value eventually
        if len(filtered_by_difficulty) == 0:
            continue

        if i == 3 and len(filtered_by_difficulty) >= 2:
            temp_name = sample(filtered_by_difficulty, 2)
            captcha_quiz_order.append(temp_name.pop())
            captcha_quiz_order.append(temp_name.pop())
        else:
            captcha_quiz_order.append(sample(filtered_by_difficulty, 1).pop())

    return captcha_quiz_order
