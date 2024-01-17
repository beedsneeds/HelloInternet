from django.apps import AppConfig


class CaptchapracticeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "captchapractice"

    def ready(self):
        from . import signals
