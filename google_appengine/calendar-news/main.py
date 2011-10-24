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
from MadAlchemy import Alchemy, multidict
from MadBing import Bing

SETTINGS = {
	'APP_NAME': 'nucalendarfeed',
	'CONSUMER_KEY':'nucalendarfeed.appspot.com',
	'CONSUMER_SECRET': 'wYhmmHnVDHpinMNG3KZwNwee',
	'SCOPES' : ['https://www.google.com/calendar/feeds']
}

client = gdata.calendar.client.CalendarClient(source = 'nucalendarfeed')
a = Alchemy('api_keys.txt')
b = Bing('api_keys.txt')


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
    query.max_results = 3
    query.ctz = 'America/Chicago'
    feed = client.GetCalendarEventFeed(q=query)
    ret_dict = {}
    for i, an_event in enumerate(feed.entry):
      event_dict = {'Person':[],'City':[],'Company':[],'Facility':[],'Organization':[],'StateOrCountry':[],}
      accumlator = ''
      title_dict = {'Person':[],'City':[],'Company':[],'Facility':[],'Organization':[],'StateOrCountry':[],}
      body_dict = {'Person':[],'City':[],'Company':[],'Facility':[],'Organization':[],'StateOrCountry':[],}
      where_dict = {'Person':[],'City':[],'Company':[],'Facility':[],'Organization':[],'StateOrCountry':[],}

      if an_event.title.text is not None:
	txt = a.getRankedTxtEntities(an_event.title.text)
	json_dict = json.loads(txt)
        for entity in json_dict['entities']:
	  if entity['type'] == 'Person':
            title_dict['Person'].append(entity['text'])
	  elif entity['type'] == 'City':
            title_dict['City'].append(entity['text'])
          elif entity['type'] == 'Company':
            title_dict['Company'].append(entity['text'])
          elif entity['type'] == 'Facility':
            title_dict['Facility'].append(entity['text'])
	  elif entity['type'] == 'Organization':
            title_dict['Organization'].append(entity['text'])
	  elif entity['type'] == 'StateOrCounty':
            title_dict['StateOrCountry'].append(entity['text'])

      if an_event.content.text is not None:
	txt = a.getRankedTxtEntities(an_event.title.text)
	json_dict = json.loads(txt)
        for entity in json_dict['entities']:
	  if entity['type'] == 'Person':
            body_dict['Person'].append(entity['text'])
	  elif entity['type'] == 'City':
            body_dict['City'].append(entity['text'])
          elif entity['type'] == 'Company':
            body_dict['Company'].append(entity['text'])
          elif entity['type'] == 'Facility':
            body_dict['Facility'].append(entity['text'])
	  elif entity['type'] == 'Organization':
            body_dict['Organization'].append(entity['text'])
	  elif entity['type'] == 'StateOrCounty':
            body_dict['StateOrCountry'].append(entity['text'])

      for place in an_event.where:
        txt = a.getRankedTxtEntities(place.value)
	json_dict = json.loads(txt)
        for entity in json_dict['entities']:
	  if entity['type'] == 'City':
            where_dict['City'].append(entity['text'])
          elif entity['type'] == 'Company':
            where_dict['Person'].append(entity['text'])
          elif entity['type'] == 'Facility':
            where_dict['Person'].append(entity['text'])
	  elif entity['type'] == 'Organization':
            where_dict['Person'].append(entity['text'])
	  elif entity['type'] == 'StateOrCounty':
            where_dict['Person'].append(entity['text'])

      chk = lambda d: d[0] + ' ' if len(d) > 0 else ''
      final_dict = {}
      search_string = chk(title_dict['Person'])  + chk(title_dict['StateOrCountry'])  + chk(where_dict['City'])  +  chk(title_dict['Organization'])
      if search_string != '':
        search = b.getNewsResults(search_string)
        search_dict = json.loads(search)
	tzt = search_dict['SearchResponse']
	if 'News' in tzt:
          final_dict['title_news'] = tzt['News']['Results']
	search2 = b.getWebResults(search_string)
        search_dict = json.loads(search2)
	final_dict['title_search'] = search_dict['SearchResponse']['Web']['Results']
      search_string = chk(title_dict['Organization']) +  chk(body_dict['Organization']) +  chk(title_dict['Company']) + chk(body_dict['Company'])
      if search_string != '':
        search = b.getNewsResults(search_string)
        search_dict = json.loads(search)
	if 'News' in search_dict['SearchResponse']:
	  final_dict['company_news'] = search_dict['SearchResponse']['Web']['Results']
      ret_dict[an_event.title.text] = final_dict
    print json.dumps(ret_dict)


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
