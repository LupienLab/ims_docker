# user_profiles/utils.py

from .models import UserProfile

def is_admin(user):
  """Check if the user is an admin."""
  return user.groups.filter(name='admin_access').exists()

def is_supervisor(user):
    """Check if the user is a supervisor."""
    return user.groups.filter(name='Supervisors').exists()

def is_admin_or_is_supervisor(user):
    """Check if the user is a supervisor or admin."""
    return is_admin(user) or is_supervisor(user)

def is_sequence_core(user):
    """Check if the user is a sequence core user."""
    return user.groups.filter(name='sequence_core').exists()

def get_user_lab(user):
  """
  Retrieve the lab associated with the given user.

  Args:
      user (User): The user instance for which to retrieve the lab.

  Returns:
      Lab or None: The associated Lab instance or None if no lab is assigned.
  """
  try:
      user_profile = UserProfile.objects.get(user=user)
      return user_profile.lab  # This will return None if lab is not assigned
  except UserProfile.DoesNotExist:
      return None  # Return None if the user does not have a profile
