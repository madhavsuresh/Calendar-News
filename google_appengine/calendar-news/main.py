#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import os
import urllib
import cgi
import pickle
import oauth2 as oauth
from mad.MadBing import Sentinal
from mad.rfc3339 import rfc3339
from datetime import datetime


from apiclient.discovery import build
from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName
from google.appengine.ext.webapp import template
from oauth2client.client import OAuth2WebServerFlow
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import login_required


FLOW = OAuth2WebServerFlow(
    # Visit https://code.google.com/apis/console to
    # generate your client_id, client_secret and to
    # register your redirect_uri.
    client_id='498598150569.apps.googleusercontent.com',
    client_secret='PbX0GdoYj8c3jq0EUl3il1oU',
    scope='https://www.googleapis.com/auth/calendar.readonly',
    user_agent='calendarnews/alpha')

LINKEDIN = {'GLOBAL_KEY':'cqgmvmqtxn3z', 'GLOBAL_SECRET': 'cQs7wMCRtnoLPZmK'}

consumer = oauth.Consumer(LINKEDIN['GLOBAL_KEY'],LINKEDIN['GLOBAL_SECRET'])


class Credentials(db.Model):
  credentials = CredentialsProperty()

class LinkedInCred(db.Model):
    user_key = db.ByteStringProperty()
    user_secret = db.ByteStringProperty()

class PersonalNotes(db.Model):
     




class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    user_id = user.user_id()
    credentials = StorageByKeyName(
        Credentials,user_id, 'credentials').get()
    lCred = LinkedInCred.get_by_key_name(user_id)

    if credentials is None or credentials.invalid == True:
      callback = self.request.relative_url('/oauth2callback')
      authorize_url = FLOW.step1_get_authorize_url(callback)
      memcache.set(user_id + 'goog', pickle.dumps(FLOW))
      self.redirect(authorize_url)
    elif lCred is None:
      user = users.get_current_user()
      request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
      client = oauth.Client(consumer)
      callback = self.request.relative_url('/linkedin')
      resp,content = client.request(request_token_url,"POST",body=urllib.urlencode({'oauth_callback':callback}))
      request_token = dict(cgi.parse_qsl(content))
      memcache.set(user_id + 'linked',pickle.dumps(request_token))
      authorize_url = 'https://api.linkedin.com/uas/oauth/authorize?oauth_token=%s&oauth_callback=%s' % (request_token['oauth_token'],'http://localhost:8080/linkedin')
      self.redirect(authorize_url)
    else:

      http = httplib2.Http()
      http = credentials.authorize(http)
      service = build("calendar", "v3", http=http)
      date = datetime.now()
      rfc_stamp = rfc3339(date)
      events = service.events().list(calendarId='primary',singleEvents=True,orderBy='startTime',
                                    maxResults=5,timeMin=rfc_stamp).execute()
      s = Sentinal(lCred.user_key,lCred.user_secret)

      sidebar = []
      
      getID = self.request.get('getID')
      sq = None

      for event in events['items']:
          if getID == event['id']:
              sq = event['summary']
          sidebar.append({'id':event['id'],'name':event['summary']})

      if sq is None:
          getID = sidebar[0]['id']
          sq = sidebar[0]['name']
      entities = sq.split(',')
      
      cache_get = memcache.get(getID)
      if cache_get:
          resp = pickle.loads(cache_get)
      else:
        if(len(entities) < 2):
            self.redirect('http://i.imgur.com/mvXs4.png')
            return
        resp = s.createResponse(sidebar,entities[0],entities[1])
        memcache.set(getID,pickle.dumps(resp),time=600)

      path = os.path.join(os.path.dirname(__file__),'tesdex.html')
      self.response.out.write(template.render(path,resp))

class AddNotes(webapp.RequestHandler):
    def post(self):
        
class LinkedInAuth(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        request_token = pickle.loads(memcache.get(user.user_id()+ 'linked'))
        access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
        auth_verifier = self.request.get('oauth_verifier')
        token = oauth.Token(request_token['oauth_token'],request_token['oauth_token_secret'])
        token.set_verifier(auth_verifier)
        client = oauth.Client(consumer,token)
        resp,content = client.request(access_token_url,'POST')
        tokens = dict(cgi.parse_qsl(content))
        cred = LinkedInCred(key_name=user.user_id(),user_key=tokens['oauth_token'],
                                    user_secret=tokens['oauth_token_secret'])
        cred.put()
        self.redirect('/calendarnews')

class OAuthHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    flow = pickle.loads(memcache.get(user.user_id() + 'goog'))
    if flow:
      credentials = flow.step2_exchange(self.request.params)
      StorageByKeyName(
          Credentials, user.user_id(), 'credentials').put(credentials)
      self.redirect("/calendarnews")
    else:
      pass


def main():
  application = webapp.WSGIApplication(
      [
      ('/calendarnews', MainHandler),
      ('/oauth2callback', OAuthHandler),
      ('/linkedin',LinkedInAuth),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
