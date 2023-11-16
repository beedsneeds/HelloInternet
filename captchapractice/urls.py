from django.urls import path
from . import views

app_name = "captchapractice"
urlpatterns = [
    path("", views.index, name='index'),
    path("begin/",  views.begin, name='begin' ), 
    path("<int:image_id>/",  views.selection, name='selection' ), 
    path("<int:image_id>/result/",  views.result, name='result' ), 



    # path("<int:image_id>/results/",  views.result, name='result' ),



    # path("<int:question_id>/results/", views.results, name="results"),


]