from django.shortcuts import redirect
from django.urls import reverse, resolve

from user_profiles.utils import is_sequence_core

import re

class ApprovalsAccessMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    # Check if the user is authenticated and user belongs to the 'sequence_core' group
    if request.user.is_authenticated and is_sequence_core(request.user):
      # Redirect login to approval_list for sequence_core users
      if self.is_login_path(request):
        return redirect(reverse('approval_list'))

      # If the requested path is not the allowed path, redirect to access denied
      if not self.is_allowed_path(request):
        return redirect(reverse('access_denied'))

    response = self.get_response(request)
    return response

  def is_login_path(self, request):
      """Check if current path matches login URL"""
      try:
          login_match = resolve(request.path_info)
          return login_match.url_name == 'login'
      except:
          return False

  def is_allowed_path(self, request):
      """Check if path matches allowed URL names or patterns"""
      allowed_url_names = {
          'approval_list',
          'complete_request',
          'access_denied',
          'login',
          'logout',
          'profile'
      }


      # Method 1: Check by URL name (handles URL parameters)
      try:
          match = resolve(request.path_info)
          if match.url_name in allowed_url_names:
              return True
      except:
          pass

      # Method 2: Regex fallback for complete/<int:pk>/
      if re.match(r'^complete/\d+/$', request.path_info):
          return True

      return False
