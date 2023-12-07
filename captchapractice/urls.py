from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


app_name = "captchapractice"
urlpatterns = [
    path("", views.home, name="home"),
    # path("", views.index, name='index'),
    path("index/", views.index, name='index'),
    path("begin/",  views.begin, name='begin' ), 
    path("<int:image_id>/",  views.selection, name='selection' ), 
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)