from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import login, logout
from keycloak import KeycloakOpenID
from django.contrib import messages

# Initialize Keycloak client
keycloak_openid = KeycloakOpenID(server_url=settings.KEYCLOAK_SERVER_URL,
                                  client_id=settings.KEYCLOAK_CLIENT_ID,
                                  realm_name=settings.KEYCLOAK_REALM,
                                  client_secret_key=settings.KEYCLOAK_CLIENT_SECRET)

def login_view(request):
    # Redirect to Keycloak login
    return redirect(keycloak_openid.auth_url(redirect_uri=settings.KEYCLOAK_REDIRECT_URI, scope='openid'))

def callback_view(request):
  # Get the authorization code from the request
  code = request.GET.get('code')
  if code:
    # Exchange the authorization code for tokens
    token = keycloak_openid.token(
      grant_type='authorization_code',
      code=code,
      redirect_uri=settings.KEYCLOAK_REDIRECT_URI,
      scope='openid')
    # Use the access token to get user info
    user_info = keycloak_openid.userinfo(token['access_token'])

    # Log the user in (you may want to create a user in your Django app)
    # Here, you can create or update the user in your Django app
    # For simplicity, we are just logging in the user
    request.session['user'] = user_info
    return redirect('home')  # Redirect to a home page or dashboard
  else:
    messages.error(request, 'Authentication failed.')
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('http://localhost:8080/auth/realms/myrealm/protocol/openid-connect/logout?redirect_uri=http://localhost:8000/accounts/login/')
