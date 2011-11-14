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
from google.appengine.ext import db

from google.appengine.api import oauth
import time

from collections import defaultdict
import urllib2
import urllib
import gdata.gauth
import gdata.calendar.client
import os
from mad.MadBing import Bing, StockChecker, WolframAlpha,LinkedIn

SETTINGS = {
	'APP_NAME': 'nucalendarfeed',
	'CONSUMER_KEY':'nucalendarfeed.appspot.com',
	'CONSUMER_SECRET': 'wYhmmHnVDHpinMNG3KZwNwee',
	'SCOPES' : ['https://www.google.com/calendar/feeds']
	
}

client = gdata.calendar.client.CalendarClient(source = 'nucalendarfeed')
#a = Alchemy('api_keys.txt')
b = Bing('api_keys.txt')
s = StockChecker()
w = WolframAlpha('api_keys.txt')
l = LinkedIn()



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

class CalUser(db.Model):
  user = db.UserProperty()
  linkedinKey = db.ByteStringProperty()
  linkedinSecret = db.ByteStringProperty()


class Event(db.Model):
  event_id = db.IntegerProperty()
  company = db.StringProperty()

class PackInfo(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__),'appointment_maker.html')
    self.response.out.write(template.render(path,0))

  def post(self):
    ret_dict = {}
    person = self.request.get('person')
    company = self.request.get('company')
    ret_dict['person'] = person
    ret_dict['company'] = company
    stock_symbol = s.Check(company)
    bing_news  = json.loads(b.getNewsResults(company,4))
    ret_dict['bing_news']= bing_news['SearchResponse']['News']['Results']

    personal_info = json.loads(l.getPersonInfo(person))
    ret_dict['personal_info'] = personal_info

    if stock_symbol != '':
      num_employees =  w.getNumEmployees(stock_symbol)
      stock_img =  w.getStockImg(stock_symbol)
      stock_price = w.getStockPrice(stock_symbol)
      ret_dict['financial_data'] = {'num_employees' : num_employees,'stock_img' : stock_img,
			'stock_symbol' : stock_symbol,'stock_price' : stock_price}


    path = os.path.join(os.path.dirname(__file__),'tesdex.html')
    self.response.out.write(template.render(path,ret_dict))



    
class TestingUsers(webapp.RequestHandler):
  @util.login_required
  def get(self):
    current_user = users.get_current_user()
    print current_user

class GoogleAuth(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__),'static/googleauth.html')
    self.response.out.write(template.render(path,0))
  

def main():
  application = webapp.WSGIApplication([('/calendarnews/PackInfo',PackInfo),
					('/google0966cae5fafeed54.html',GoogleAuth),],
                                        debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
