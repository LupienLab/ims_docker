from keycloak import KeycloakOpenID
#from django.shortcuts import render, get_object_or_404, redirect
#from keycloak import KeycloakAdmin

# Keycloak configuration
KEYCLOAK_SERVER_URL = 'https://oa.pmgenomics.ca/auth/'
REALM_NAME = 'Techna'
CLIENT_ID = 'ankita-dev'
CLIENT_SECRET = 'ae1fc7b3-8253-479b-8135-33d94ebaacc9'

# Create Keycloak client instance
keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                                 client_id=CLIENT_ID,
                                 realm_name=REALM_NAME,
                                 client_secret_key=CLIENT_SECRET)

# Function to get Keycloak user token
def get_keycloak_url(request):
    # Get WellKnown
    config_well_known = keycloak_openid.well_known()
    #login_url = keycloak_openid.auth_url('http://172.27.164.206:5050/')
    login_url = keycloak_openid.auth_url('http://localhost:8000/')
    
    return (login_url)

# Function to get Keycloak user token
def get_keycloak_user_token(request):
    code = request.GET.get('code')
    #print("code",code)
    user_token = keycloak_openid.token(
            grant_type='authorization_code',
            code=code,
            redirect_uri="http://localhost:8000/")
    
    userinfo = keycloak_openid.userinfo(user_token["access_token"])

    # print(user_token)
    # print(user_token["access_token"])
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
