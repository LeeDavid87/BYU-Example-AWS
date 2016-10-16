import requests
from flask import redirect, request, json
from urllib import urlencode
from urlparse import parse_qs
from functools import wraps
from urllib2 import Request, urlopen, URLError

class GitHub(object):
    BASE_URL = 'https://api.github.com/'
    BASE_AUTH_URL = 'https://github.com/login/oauth/'
    

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.initGithub(self.app)
        else:
            self.app = None
    # Inits the github app
    def initGithub(self, app):
        self.client_id = app.config['CLIENT_ID']
        self.client_secret = app.config['CLIENT_SECRET']
        self.base_url = app.config.get('BASE_URL', self.BASE_URL)
        self.auth_url = app.config.get('AUTH_URL', self.BASE_AUTH_URL)
        self.session = requests.session()

    # Get logged in user     
    def getUser(self, oauth_token):
        url = self.base_url + "user?" + urlencode(oauth_token)
        user = self.getData(url, oauth_token)
        return user['login']
        
    # get organization of logged in user    
    def getOrg(self, user, oauth_token):
        url = self.base_url + "users/" + user + "/orgs?" + urlencode(oauth_token)
        org = self.getData(url, oauth_token)
        if org[0] is not None:
            return org[0]['login']
        else:
            return None

    # Get members of the organization       
    def getMembers(self, org, oauth_token):
        url = self.base_url + "orgs/" + org + "/members?" + urlencode(oauth_token)
        members = self.getData(url, oauth_token)
        memberMap = {}
        for member in members:
            name = self.getName(member['login'], oauth_token)
            user = member['login']
            if name is not None:
                memberMap[ user ] = name
            else:
                memberMap[ user ] = None
        return memberMap

    # Get the number of a member from the organization      
    def getName(self, user, oauth_token):
        url = self.base_url + "users/" + user + "?" +urlencode(oauth_token)
        member = self.getData(url, oauth_token)
        return member['name']
        
    # Gets the email of each member in the organization
    def getEmail(self, user, oauth_token):
        url = self.base_url + "users/" + user + "?" + urlencode(oauth_token)
        email = self.getData(url, oauth_token)
        return email['email']
   
    # Pull data from Json API request
    def getData(self, url, oauth_token):
        request  = Request(url)
        response = urlopen(request)
        data     = json.loads(response.read())
        return data
       
    
    # Authorize login    
    def authorize(self, scope):
        params = {'client_id': self.client_id, 'scope' : scope}
        url = self.auth_url + 'authorize?' + urlencode(params)
        return redirect(url)

    # get the token with login creds    
    def getToken(self, token):
        @wraps(token)
        def decorated(*args, **kwargs):
            if 'code' in request.args:
                params = {
                'code': request.args.get('code'),
                'client_id': self.client_id,
                'client_secret': self.client_secret}
                url = self.auth_url + 'access_token'
                response = self.session.post(url, data=params)
                data = parse_qs(response.content)
            else:
                data = self._handle_invalid_response()
            return token(*((data['access_token'][0],) + args), **kwargs)
        return decorated