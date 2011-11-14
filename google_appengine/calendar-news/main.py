#
#!/usr/bin/env python
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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

from collections import defaultdict
import urllib2
import urllib
import gdata.gauth
import gdata.calendar.client
import os
from mad.MadBing import Bing

SETTINGS = {
	'APP_NAME': 'nucalendarfeed',
	'CONSUMER_KEY':'nucalendarfeed.appspot.com',
	'CONSUMER_SECRET': 'wYhmmHnVDHpinMNG3KZwNwee',
	'SCOPES' : ['https://www.google.com/calendar/feeds']
}

client = gdata.calendar.client.CalendarClient(source = 'nucalendarfeed')
#a = Alchemy('api_keys.txt')
b = Bing('api_keys.txt')


class CompanyProfile(db.Model):
	req_date = db.DateTimeProperty()
  name = db.ByteStringProperty()
	logo = db.LinkProperty()
	num_employees = db.IntegerProperty()
	stock_price = db.FloatProperty()
	stock_graph = db.LinkProperty()

class PersonalProfile(db.Model):
  linkedinID = db.ByteStringProperty() 
	firstName = db.ByteStringProperty()
	lastName = db.ByteStringProperty()
	education = db.StringProperty()
	location = db.StringProperty()
	position = db.StringProperty()
	pastPositions = db.StringProperty()


class Event(db.Model):
  event_id = db.IntegerProperty()
	company = db.StringProperty()

class 

class Fetcher(webapp.RequestHandler):
  @util.login_required
  def get(self):

    current_user = users.get_current_user()
    
    if current_user:

      oauth_callback_url = 'http://%s/get_access_token' % self.request.host
      request_token = client.GetOAuthToken(SETTINGS['SCOPES'],oauth_callback_url,
				         SETTINGS['CONSUMER_KEY'],
					 consumer_secret = SETTINGS['CONSUMER_SECRET'])

      request_token_key = 'request_token_%s' % current_user.user_id()
      gdata.gauth.ae_save(request_token,request_token_key)

      approval_page_url = request_token.generate_authorization_url()

      message = """<a href="%s">
Request Token for the Google Documents Scope</a>"""
      self.response.out.write(message % approval_page_url)
    else:
      greeting = ("<a href=\"%s\" Sign in plz </a>." % users.create_login_url("/auth"))
            
      

class RequestTokenCallback(webapp.RequestHandler):
  
  @util.login_required
  def get(self):
 
    current_user = users.get_current_user()
    request_token_key = 'request_token_%s' % current_user.user_id()
    request_token = gdata.gauth.AeLoad(request_token_key)
    gdata.gauth.AuthorizeRequestToken(request_token, self.request.uri)
    client.auth_token = client.GetAccessToken(request_token)
    access_token_key = 'access_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(request_token,access_token_key)


    query = gdata.calendar.client.CalendarEventQuery()
    query.orderby = 'starttime'
    query.futureevents = 'true'
    query.singleevents = 'true'
    query.sortorder = 'a'
    query.max_results = 8
    query.ctz = 'America/Chicago'
    feed = client.GetCalendarEventFeed(q=query)
    ret_dict = {}
    for i, an_event in enumerate(feed.entry):
      print an_event.title.text
      print an_event.id

class GoogleAuth(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__),'static/googleauth.html')
    self.response.out.write(template.render(path,0))
  

def main():
  application = webapp.WSGIApplication([('/auth',Fetcher),
					('/get_access_token',RequestTokenCallback),
					('/google0966cae5fafeed54.html',GoogleAuth),],
                                        debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
