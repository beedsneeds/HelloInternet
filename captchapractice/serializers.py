from django.contrib.auth.models import User
from .models import CaptchaImage
from rest_framework import serializers

class CaptchaImageSerializer(serializers.HyperlinkedModelSerializer):
    
    # def create(self, validated_data): to create a model instance

    url = serializers.URLField(source="get_absolute_url")
    slice_list = serializers.JSONField(source="api_get_img_slice_list_as_json")
    
    class Meta:
        model = CaptchaImage
        # fields = "__all__" this doesn't work
        fields = [
            "image_name", 
            "prompt_text", 
            "slice_count", 
            "difficulty_level", 
            "pk", 
            "url",
            "slice_list",
        ]

