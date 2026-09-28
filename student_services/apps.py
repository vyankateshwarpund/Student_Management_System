"""Student services app configuration."""
from django.apps import AppConfig


class StudentServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'student_services'
    verbose_name = 'Student Services & Campus Life'
