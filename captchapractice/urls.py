from django.urls import path, include
from . import views
from rest_framework import routers

from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'captcha', views.CaptchaImageViewSet)

app_name = "captchapractice"
urlpatterns = [
    path("", views.home, name="home"),
    path("index/", views.image_index, name="index"),
    path("begin/", views.begin, name="begin"),
    path("<int:image_id>/", views.selection, name="selection"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("end/", views.end, name="end"),
    path("empty/", views.empty, name="empty"),
    path("new/", views.new_captcha, name="new"),
    path("newtwo/", views.new_captcha_details, name="newtwo"),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
