import json
from Automate import Automate
from flask import Flask, render_template, render_template_string, g, redirect
from Github_Auth import GitHub
app = Flask(__name__)


# value for github
CLIENT_ID = 'dcd54f04483f284f7dfc'
CLIENT_SECRET = '7e8419e55f76da4638bfec09ee7e1af9589e6f47'
auth_url = 'https://github.com/login/oauth/authorize'

# valuse for AWS
ACCESS_KEY_ID = 'AKIAIZUVBZIKHQLPOU4A'
SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'github-accounts'

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# init Github class
github = GitHub(app)

# init auto class
automate = Automate(app)

# Main page
@app.route('/')
def main():
    return render_template("index.html")

# After authorized    
@app.route('/log-auth')
@github.getToken
def authorized(oauth_token):
    oauth_token = {'access_token' : oauth_token}
    user    = github.getUser(oauth_token)
    org     = github.getOrg(user, oauth_token)
    if org is not None:
        members = github.getMembers(org, oauth_token)
        nameless = namelessMember(members)
        sendEmails(nameless, oauth_token)
        link = automate.getLink()
        return render_template("log-auth.html", user=user, org=org, members=members, nameless=nameless, link=link)
    else:
        return render_template("no-org.html")

# Sends emails to each person without a name
def sendEmails(nameless, oauth_token):
    automate.sendToAws(nameless)
    for UID in nameless:
        email = github.getEmail(UID, oauth_token)
        if email is not None:
            automate.sendEmail(UID, email)
	
# Pulls all members without a name out
def namelessMember(members):
    names = members.copy()
    for key, value in members.iteritems():
        if value is not None:
           del names[key]
    return names
        
# Takes you to login page
@app.route('/login')
def login():
    return github.authorize(scope="admin:org")
    
if __name__ == "__main__":
    app.run()
