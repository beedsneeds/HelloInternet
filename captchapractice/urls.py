from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


app_name = "captchapractice"
urlpatterns = [
    path("", views.home, name="home"),
    # path("", views.index, name='index'),
    path("index/", views.index, name="index"),
    path("begin/", views.begin, name="begin"),
    path("<int:image_id>/", views.selection, name="selection"),

    path("login/", views.login_view, name="login"), 
    path("signup/", views.signup_view, name="signup"), 
    path("logout/", views.logout_view, name="logout"), 
 
    path("end/", views.end, name="end"),
    path("empty/", views.empty, name="empty"),
    
    path("new/", views.new_captcha, name="new"),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
