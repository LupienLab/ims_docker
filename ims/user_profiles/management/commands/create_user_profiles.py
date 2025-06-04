from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_profiles.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            UserProfile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created UserProfiles for existing users.'))
