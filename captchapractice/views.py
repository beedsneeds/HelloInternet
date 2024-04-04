from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template import loader

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user, login, logout, authenticate

from .models import CaptchaImage, UserResponses, get_captcha_order
from .forms import SignupForm, LoginForm, NewCaptchaForm_Upload, NewCaptchaForm_Details

from .utils import validate_image_dimensions, run_object_detection, make_image_slices

import json


# These two have to be replaced by generic views.
def end(request):
    template = loader.get_template("captchapractice/end.html")
    context = {}
    return HttpResponse(template.render(context, request))


def empty(request):
    template = loader.get_template("captchapractice/empty.html")
    context = {}
    return HttpResponse(template.render(context, request))


def home(request):
    context = None
    return render(request, "captchapractice/home.html", context)


# Start here or you can view the captcha gallery (index) and pick what captcha to solve


# Rename to image index
# add pagination here
def index(request):
    template = loader.get_template("captchapractice/index.html")

    captchalist = CaptchaImage.objects.order_by("-difficulty_level")[:15]
    context = {
        "captchalist": captchalist,
    }
    return HttpResponse(template.render(context, request))


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
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("captchapractice:home"))

    login_form = LoginForm()
    signup_form = SignupForm()
    # This page houses the signup_form as well. The post request of the signup_form is directly sent to /signup
    context = {
        "login_form": login_form,
        "signup_form": signup_form,
    }
    return HttpResponse(template.render(context, request))


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password1 = form.cleaned_data["password1"]
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
            return redirect("captchapractice:home")

    return redirect("captchapractice:login")


def logout_view(request):
    logout(request)
    return redirect(reverse("captchapractice:home"))


"""
Process 

page 3:
    - slice images + element presence
    - link to the finished prompt
"""


def new_captcha(request):
    """
    Page 1 (of 3) of Captcha creation:
    - GET:
        upload imagefile
        image name
    - POST:
        handle form
        run img validation
        run yolo8
    """

    if request.method == "POST":
        upload_form = NewCaptchaForm_Upload(request.POST, request.FILES)

        if upload_form.is_valid():
            filename = upload_form.cleaned_data["filename"]
            result = validate_image_dimensions(
                image=request.FILES["image"], filename=filename
            )
            if result is True:
                detected_coords, detected_classes = run_object_detection(filename)

                request.session["detected_classes"] = detected_classes
                request.session["detected_coords"] = detected_coords
                request.session["filename"] = filename

                template = loader.get_template(
                    "captchapractice/new_captcha_details.html"
                )
                details_form = NewCaptchaForm_Details(detected_classes=detected_classes)
                context = {
                    "filename": filename,
                    "details_form": details_form,
                }

                return HttpResponse(template.render(context, request))
        else:
            print("form.errors:", upload_form.errors)
            print("form.non_field_errors", upload_form.non_field_errors)

    upload_form = NewCaptchaForm_Upload()
    template = loader.get_template("captchapractice/new_captcha_upload.html")
    context = {
        "upload_form": upload_form,
    }

    return HttpResponse(template.render(context, request))


def new_captcha_details(request):
    """
    Page 2 (of 3) of Captcha creation:
    - GET: (continuation of Page 1 POST)
        Display yolo8 output
        object selection options (built into prompt text)
        slice count
        difficulty rating
    - POST:
        handle form
        create image slices incl. computing element presence
    """

    detected_classes = request.session.get("detected_classes")
    detected_coords = request.session.get("detected_coords")
    filename = request.session.get("filename")

    if request.method == "POST":
        details_form = NewCaptchaForm_Details(
            request.POST, detected_classes=detected_classes
        )
        if details_form.is_valid():
            selected_object = details_form.cleaned_data["selected_object"]

            captcha_image = CaptchaImage.objects.create(image_name=filename)
            captcha_image.prompt_text = f"Select the {selected_object} in the image"
            captcha_image.slice_count = details_form.cleaned_data["slice_count"]
            captcha_image.difficulty_level = details_form.cleaned_data[
                "difficulty_level"
            ]
            captcha_image.save()
            # After the image is saved, a post-save signal is sent to signals.py\
            make_image_slices(
                captcha_instance=captcha_image,
                detected_coords=detected_coords,
                selected_object=selected_object,
            )
            print("making pizza slices")
        else:
            print("form.errors:", details_form.errors)
            print("form.non_field_errors", details_form.non_field_errors)

    # will not be reachable when not testing individual pages
    template = loader.get_template("captchapractice/new_captcha_details.html")
    detected_classes = {
        ("potato", "potato"),
    }
    details_form = NewCaptchaForm_Details(detected_classes=detected_classes)
    context = {
        "filename": "shikamaru",
        "details_form": details_form,
    }

    return HttpResponse(template.render(context, request))


def new_captcha_review(request):
    """
    TODO 1:1 Validation error reporting
    TODO return if non-unique image_name provided
    TODO not boring prompt list. 'Highlight, pick'
    TODO # V imp test: If slice isn't a 4 elem tuple of ints and if mask isn't a 2 elem nested list of lists
    TODO # handle the logic of 'username & password does not match' and (optional) 'username doesn't exist'
    TODO change to yolo large in production

    """
    pass
