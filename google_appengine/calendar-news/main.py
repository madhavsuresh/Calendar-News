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
from calais import Calais
import gdata.gauth
import gdata.calendar.client
import os

SETTINGS = {
	'APP_NAME': 'nucalendarfeed',
	'CONSUMER_KEY':'nucalendarfeed.appspot.com',
	'CONSUMER_SECRET': 'wYhmmHnVDHpinMNG3KZwNwee',
	'SCOPES' : ['https://www.google.com/calendar/feeds']
}

CALAIS_API_KEY = 'qztg59a6ghx8aqh8txgccm3x'

calais = Calais(CALAIS_API_KEY, submitter='nucalendarfeed')


client = gdata.calendar.client.CalendarClient(source = 'nucalendarfeed')


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
    query.sortorder = 'a'
    query.futureevents = 'true'
    query.max_results = 2
    feed = client.GetCalendarEventFeed(q=query)
    print 'Events on Primary Calendar: %s' % (feed.title.text,)
    print len(feed.entry)

    accumlator = ''
    for i, an_event in enumerate(feed.entry):
      print '\t%s. %s' % (i, an_event.title.text,)
      print '\t%s. %s' % (i, an_event.content.text,)
      accumlator+= an_event.title.text;

    result = calais.analyze(accumlator)
    result.print_summary()
    


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
