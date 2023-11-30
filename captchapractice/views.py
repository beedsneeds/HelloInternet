from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template import loader

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user

from .models import CaptchaImage, UserResponses

import json


def home(request):

    context = None
    return render(request, "captchapractice/home.html", context)

# start here or you can view the captcha gallery (index) and pick what captcha to solve 


# rename to image index
def index(request):
    template = loader.get_template("captchapractice/index.html")

    captchalist = CaptchaImage.objects.order_by("-difficulty_level")[:15]
    context = {
        "captchalist": captchalist,
    }

    return HttpResponse(template.render(context, request))

# add pagination here


def begin(request):
    template = loader.get_template("captchapractice/begin.html")

    img_slice_list = [
        "gojo_1", "gojo_2", "gojo_3",
        "gojo_4", "gojo_5", "gojo_6",
        "gojo_7", "gojo_8", "gojo_9", 
    ]
    
    prompt = "Select nanami"

    context = {
        "img_slice_list": img_slice_list,
        "prompt": prompt,
        }

    return HttpResponse(template.render(context, request))


@login_required
def selection(request, image_id):

    img_object = get_object_or_404(CaptchaImage, pk=image_id)
    img_slice_list = img_object.get_img_slice_list(image_id=image_id)

    if request.method == "POST":
        try: 
            selected_images = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as err:
            return JsonResponse({'status': 'error', 'message': str(err)}, status=400)
        
        # if selected_images != []:  # is there a better way to validate input?
        # I'm currently not validating this because its entering from JS, I'll do it later
            
        # saving to db
        response = UserResponses.objects.create(root_image=img_object)
        response.response_json = json.dumps(selected_images)
        response.user = get_user(request)
        response.save()

        #testing for correctness
        correct_choices = img_object.correct_choices(image_id=image_id)

        if set(selected_images) == set(correct_choices):
            correctness_check = "you are correct"
        else:
            correctness_check = "you got it wrong"
        
        #  temp place where I put this
        set_response = set(selected_images)
        set_correct_choices = set(correct_choices)
        correct_responses = set_correct_choices & set_response
        wrong_responses = set_response - set_correct_choices
        unselected_correct_r = set_correct_choices - set_response
        
        # adding context
        context = {
            "selected_images": selected_images,
            "correct_choices": correct_choices, 
            "correctness_check": correctness_check,  # these 3 can be removed / rationalized

            "img_slice_list": img_slice_list,
            "correct_responses": correct_responses,
            "wrong_responses": wrong_responses,
            "unselected_correct_r": unselected_correct_r,
        }

        rendered_template = loader.render_to_string("captchapractice/selection.html", context)
        return JsonResponse({'html': rendered_template})
        
        # else:
        #     return JsonResponse({'error': 'Method Not Allowed'}, status=405)
                # right now I'm not letting the post request fall through to the GET request if no images are selected
                # because I'll need to handle that logic as well

        #  you can add some messsage in an else here to indicate that atleast one image should be selected


    prompt = img_object.prompt_text

    template = loader.get_template("captchapractice/selection.html")
    context = {
        "img_slice_list": img_slice_list,
        "prompt": prompt,
        "image_id": image_id,
        }

    return HttpResponse(template.render(context, request))



