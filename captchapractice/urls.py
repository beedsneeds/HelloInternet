from django.urls import path
from . import views


app_name = "captchapractice"
urlpatterns = [
    path("", views.home, name="home"),
    # path("", views.index, name='index'),
    path("index/", views.index, name='index'),
    path("begin/",  views.begin, name='begin' ), 
    path("<int:image_id>/",  views.selection, name='selection' ), 
]
