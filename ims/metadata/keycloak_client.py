from keycloak import KeycloakOpenID
import os
#from django.shortcuts import render, get_object_or_404, redirect
#from keycloak import KeycloakAdmin

# Keycloak configuration
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

# Create Keycloak client instance
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id=CLIENT_ID,
                                 realm_name=REALM_NAME,
                                 client_secret_key="Jw1zlfrbsmM7531fGK62PBtGxDXsSm5q")

# Function to get Keycloak user token
def get_keycloak_url(request):

    #login_url = keycloak_openid.auth_url('http://172.27.164.206:5050/')
    login_url = keycloak_openid.auth_url("http://localhost:8000")
    print(login_url)

    return (login_url)

# Function to get Keycloak user token
def get_keycloak_user_token(request):
    code = request.GET.get('code')
    #print("code",code)
    user_token = keycloak_openid.token(
            grant_type='authorization_code',
            code=code,
            redirect_uri="http://localhost:8000/",
            scope='openid')

    userinfo = keycloak_openid.userinfo(user_token["access_token"])

    print(user_token)
    print(user_token["access_token"])
    print(userinfo)
    request.session['user_token'] = user_token
    return (user_token,userinfo)



def logout_keycloak(request):
    token = request.session.get('user_token')
    try:
        token = keycloak_openid.refresh_token(token['refresh_token'])
        keycloak_openid.logout(token['refresh_token'])
    except:
        print("Refresh token expired")
    request.session.clear()
    request.session.flush()
    print("Session cleared")


#https://github.com/gt-novelt/python-keycloak
#https://github.com/marcospereirampj/python-keycloak
#https://github.com/marcospereirampj/python-keycloak/issues/28
