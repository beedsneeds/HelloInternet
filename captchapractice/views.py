from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template import loader, RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user, login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


from .models import CaptchaImage, UserResponses, get_captcha_order
from .forms import SignupForm, LoginForm

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


def login_view(request):
    template = loader.get_template("captchapractice/login.html")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("captchapractice:home"))
            # else:
            #     pass
                # handle the logic of 'username & password does not match' and (optional) 'username doesn't exist'

    login_form = LoginForm()
    signup_form = SignupForm()
    # This page houses the signup_form. The post request of the signup_form is directly sent to /signup
    context = {
        'login_form': login_form,
        'signup_form': signup_form,
    }
    return HttpResponse(template.render(context, request))

 
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
            return redirect('captchapractice:home')

    return redirect('captchapractice:login')

def logout_view(request):
    logout(request)
    return redirect(reverse("captchapractice:home"))

# These two have to be replaced by generic views.
def end(request):
    template = loader.get_template("captchapractice/end.html")

    context = {}

    return HttpResponse(template.render(context, request))


def empty(request):
    template = loader.get_template("captchapractice/empty.html")

    context = {}

    return HttpResponse(template.render(context, request))
