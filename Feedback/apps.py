from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Feedback'

    def ready(self):
        import Feedback.signals  #
        