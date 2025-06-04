from django.apps import AppConfig

class UserProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_profiles'

    def ready(self):
      # Import the signal handlers here to avoid circular imports
      from .signals import create_user_profile, save_user_profile
