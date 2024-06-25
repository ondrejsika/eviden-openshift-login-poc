from flask import Flask, redirect, make_response, request
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

COOKIES = {}

def get_state():
    url = 'https://console-openshift-console.apps.zbr-prod.infra.int.kpml.net/auth/login'

    session = requests.Session()

    # Send the initial request and follow redirects
    response = session.get(url, verify=False, allow_redirects=False)

    # Retrieve cookies if needed (optional, as Session handles them automatically)
    cookies = session.cookies

    print('Cookies:', cookies)

    cookiesDir = {}

    for c in cookies:
        cookiesDir[c.name] = c.value
        COOKIES[c.name] = c.value
        print('Cookie:', c.name, c.value)

    # Get the location URL from the response headers
    location_url = response.headers.get('location')

    # session.get(location_url, verify=False, allow_redirects=False)

    # Parse the location URL to get query parameters
    parsed_url = urlparse(location_url)
    query_params = parse_qs(parsed_url.query)

    # Extract the state value
    state = query_params.get('state')[0] if 'state' in query_params else None

    return state, cookiesDir


@app.route('/')
def home():
    state, cookies = get_state()
    response = make_response(redirect('/auth?state='+state))
    for key, value in cookies.items():
        response.set_cookie(key, value)
    return response
    return


@app.route('/auth')
def auth():
    state = request.args.get('state', '')
    print("!!!!!!!")
    print('COOKIES:', COOKIES)
    response = make_response(redirect('https://oauth-openshift.apps.zbr-prod.infra.int.kpml.net/oauth/authorize?client_id=console&idp=SikaLabs_SSO&redirect_uri=https%3A%2F%2Fconsole-openshift-console.apps.zbr-prod.infra.int.kpml.net%2Fauth%2Fcallback&response_type=code&scope=user%3Afull&state='+state))
    for key, value in COOKIES.items():
        response.set_cookie(key, value)
    return response

if __name__ == '__main__':
    print('http://auth.apps.zbr-prod.infra.int.kpml.net')
    app.run(debug=True, port=80)
