from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template import loader, RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user

from .models import CaptchaImage, UserResponses
from .utils import evaluate_response

import json


def home(request):

    context = None
    return render(request, "captchapractice/home.html", context)

# Start here or you can view the captcha gallery (index) and pick what captcha to solve 


# Rename to image index
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
    # remove this and see what's being used in the html

    context = {
        "img_slice_list": img_slice_list,
        "prompt": prompt,
        }

    return HttpResponse(template.render(context, request))


@login_required
def selection(request, image_id):

    img_object = get_object_or_404(CaptchaImage, pk=image_id)
    img_slice_list = img_object.get_img_slice_list(image_id=image_id)

    if request.method == "GET":

        template = loader.get_template("captchapractice/selection.html")
        context = {
            "img_slice_list": img_slice_list,
            "img_object": img_object,
            "image_id": image_id, #you can remove this as well
            }

        return HttpResponse(template.render(context, request))

    elif request.method == "POST":
        try: 
            # POST sends a json response
            selected_choices = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as err:
            return JsonResponse({'status': 'error', 'message': str(err)}, status=400)
            
        # Saving to db
        response = UserResponses.objects.create(root_image=img_object)
        response.response_json = json.dumps(selected_choices)
        response.user = get_user(request)
        response.save()

        correct_choices = img_object.correct_choices(image_id=image_id)
        # Testing for correctness; check utils.py for a breakdown
        evaluation, true_positives, false_postives, false_negatives = evaluate_response(correct_choices, selected_choices)

        context = {
            "img_slice_list": img_slice_list,
            "img_object": img_object,
            "evaluation": evaluation,
            "true_positives": true_positives,
            "false_postives": false_postives,
            "false_negatives": false_negatives,
        }

        # The view processes the post request and the corresponding response has to be loaded asynchronously.
        # Therefore, the template is rendered to string which is then loaded onto the page through DOM manipulation in JS
        rendered_template = loader.render_to_string("captchapractice/selection.html", context, request)
        return JsonResponse({'html': rendered_template})

    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)




