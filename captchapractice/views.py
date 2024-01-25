from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template import loader, RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import CaptchaImage, UserResponses, get_captcha_order, username_exists

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


@login_required
def begin(request):
    template = loader.get_template("captchapractice/begin.html")

    user = get_user(request)
    captcha_order = get_captcha_order(user)

    context = {
        "captcha_order": captcha_order,
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
        }

        return HttpResponse(template.render(context, request))

    elif request.method == "POST":
        try:
            # POST sends a json response
            selected_choices = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError as err:
            return JsonResponse({"status": "error", "message": str(err)}, status=400)

        # Saving to db
        response = UserResponses.objects.create(root_image=img_object)
        response.response_json = json.dumps(selected_choices)
        response.user = get_user(request)
        response.save()

        correct_choices = img_object.correct_choices(image_id=image_id)
        (
            evaluation,
            true_positives,
            false_postives,
            false_negatives,
        ) = UserResponses.evaluate_response(correct_choices, selected_choices)

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
        rendered_template = loader.render_to_string(
            "captchapractice/selection.html", context, request
        )
        return JsonResponse({"html": rendered_template})

    else:
        return JsonResponse({"error": "Method Not Allowed"}, status=405)


def create_new_user(request):
    if request.method == "GET":
        template = loader.get_template("create_new_user.html")
        context = {}

        return HttpResponse(template.render(context, request))

    elif request.method == "POST":
        username = request.POST.get("username")
        if username_exists(username):
            return HttpResponseRedirect(reverse("login"))

        password = request.POST.get("password")

        hashed_password = make_password(password)
        user = User.objects.create(username=username, password=hashed_password)

        login(request, user)

        # Redirect to a success page or any other appropriate action
        return HttpResponseRedirect(reverse("captchapractice:home"))


# These two have to be replaced by generic views.
def end(request):
    template = loader.get_template("captchapractice/end.html")

    context = {}

    return HttpResponse(template.render(context, request))


def empty(request):
    template = loader.get_template("captchapractice/empty.html")

    context = {}

    return HttpResponse(template.render(context, request))
