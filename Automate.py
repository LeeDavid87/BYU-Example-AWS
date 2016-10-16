import boto.s3
import sys
from boto.s3.key import Key
import smtplib
import requests
import random

class Automate(object):

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.initAutomate(self.app)
        else:
            self.app = None

    # Inits the github app
    def initAutomate(self, app):
        self.access_id = app.config['ACCESS_KEY_ID']
        self.access_secret = app.config['SECRET_ACCESS_KEY']
        self.bucket_name = app.config['BUCKET_NAME']
        self.conn = boto.connect_s3(self.access_id, self.access_secret)
        self.bucket = self.conn.get_bucket(self.bucket_name)

    # Creates and sends an email
    def sendEmail(self, user, recipient):
        gmail_user = 'test.lee.github@gmail.com'
        gmail_pwd = 'testlee123'
        FROM = 'David Lee'
        TO = recipient
        SUBJECT = 'Missing Name'
        TEXT = 'Hi %s,\n\nYour Github profile is missing a name, please follow the link to update your profile to include your name https://github.com/settings/profile' % user

        # Prepares the actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, TO, SUBJECT, TEXT)
		# Tries to connect to the server and send an email
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.close()
            print 'successfully sent email to %s' % user
        except:
            print "failed to send email to %s" % user

    # returns the link created for the names with emails sent
    def getLink(self):
        return self.link
	
	# Starts the process of sending to AWS
    def sendToAws(self, nameless):
        self.createFile(nameless)

    # Creates a file with all the members with out names
    def createFile(self, nameless):
        file = open('email_list.txt', 'w')
        for name in nameless:
            file.write(name + '\r\n')
        file.close()
        self.sendToBucket(file)
    
	# Sends the file to the AWS bucket
    def sendToBucket(self, file):
        k = Key(self.bucket)
        k.key = 'email_list_%d.txt' % random.randint(0,9000)
        file = open('email_list.txt', 'r')
        k.set_contents_from_string(file.read())
        file.close()
        k.make_public()
        self.link = 'http://s3.amazonaws.com/github-accounts/' + k.key
