#!/usr/bin/env python
# Madhav Suresh 2011

import urllib
from xml.dom import minidom
import simplejson as json
import oauth2 as oauth
from yql import YQLQuery
import re
#from google.appengine.api import oauth

class Bing():
  ''' Request object that is sent to Bing API, not all calls
  are supported right now, only the subset we need '''
  _api_key = ''
  _endpoint = 'http://api.search.live.net/json.aspx'


  def __init__(self,api_path):
    self.readAPIKey(api_path)

  def makeResponse(self,txtReq,reqType,count):
    return self._endpoint + \
	   '?Appid=' + self._api_key + \
	   '&query=' + txtReq + \
	   '&sources=' + reqType + \
	   '&' + reqType + '.count=' + str(count)

  def readAPIKey(self,fileName):
    f = open(fileName,'r')
    line = f.read().strip()
    x = dict(kvp.split('=') for kvp in line.split(';'))
    self._api_key = x['bing']

  def getNewsResults(self,txtReq,count):
    """ Return dict"""
    safe_query = urllib.quote(txtReq)
    p = self.makeResponse(safe_query,'news',count)
    result = json.loads(urllib.urlopen(p).read())
    #print result
    return result['SearchResponse']['News']['Results']

  def getTwitter(self,txtReq):
    twit_base = 'https://api.twitter.com/1'
    exp = re.compile(r'\(@(\w+)\) on Twitter')
    safe_query = urllib.quote(txtReq)
    p = self.makeResponse(safe_query,'web',10)
    result = json.loads(urllib.urlopen(p).read())
    for result in result['SearchResponse']['Web']['Results']:
      match = exp.search(result['Title'])
      if match:
        twit =  match.group(1)
        url = '%s/statuses/user_timeline.json?screen_namel=%s&count=%d' % (twit_base, twit,5)
        result = json.loads(urllib.urlopen(url).read())
        return {'handle' : twit, 'url':result['Url'],'tweets':result}
    return None

class YahooNews():
    """get yahoo news"""
    industry_url = 'http://finance.yahoo.com/rss/industry?s='
    headline_url = 'http://finance.yahoo.com/rss/headline?s='
    blog_url = 'http://finance.yahoo.com/rss/blog?s='

    def __init__(self):
        self.yql = YQLQuery()

    def getPublicNews(self,symbol,news_type,num_results):
        """Get Industry News from yahoo finance rss through YQL"""

        if news_type is "industry":
            url = self.industry_url + symbol
        elif news_type is "headline":
            url = self.headline_url + symbol
        if news_type is "blog":
            url = self.blog_url + symbol
        q = 'select * from rss where url = \'%s\'' % url
        ret =  self.yql.execute(q)
        return ret['query']['results']['item'][:num_results]

class StockChecker():

  def Check(self,query):
    safe_query = urllib.quote(query)
    url = 'http://d.yimg.com/autoc.finance.yahoo.com/' \
	   'autoc?query=%s&callback=YAHOO.Finance.SymbolSuggest.ssCallback' % (safe_query,)
    result = urllib.urlopen(url).read()
    result = result[52:-2]
    entities = json.loads(result)
    if len(entities['Result']) > 0:
      return entities['Result'][0]['symbol']
    else:
      return None
  def Price(self,symbol):
    url = 'http://www.google.com/finance/info?infotype=infoquoteall&q=%s' % (symbol)
    result = urllib.urlopen(url).read()
    info = json.loads(result[5:-2])
    return info['l']


class WolframAlpha():
  ''' Request object that is sent to Bing API, not all calls
  are supported right now, only the subset we need '''
  _api_key = ''
  _endpoint = 'http://api.wolframalpha.com/v2/query?'

  def __init__(self,api_path):
    self.readAPIKey(api_path)

  def makeResponse(self,txtReq,reqType, include):
    return self._endpoint + \
	   'appid=' + self._api_key + \
	   '&input=' + txtReq + \
	   '&format=' + reqType + \
           '&includepodid=' + include 

  def readAPIKey(self,fileName):
    f = open(fileName,'r')
    line = f.read().strip()
    x = dict(kvp.split('=') for kvp in line.split(';'))
    self._api_key = x['wolframalpha']

  def getNumEmployees(self,txtReq):
    safe_query = urllib.quote(txtReq + ' number of employees')
    p = self.makeResponse(safe_query,'plaintext', 'Result')
    result = urllib.urlopen(p).read()
    dom = minidom.parseString(result)
    x = dom.getElementsByTagName('plaintext')
    if len(x) > 0:
      return x[0].firstChild.nodeValue
    return None

  def getStockImg(self,txtReq):
    safe_query = urllib.quote(txtReq + ' stock last month')
    p = self.makeResponse(safe_query,'image,plaintext','DateRangeSpecified:Close:FinancialData')
    result = urllib.urlopen(p).read()
    dom = minidom.parseString(result)
    x = dom.getElementsByTagName('img')
    if len(x) > 0:
      return x[0].getAttribute('src')
    return None

  def getStockPrice(self,txtReq):
    safe_query = urllib.quote(txtReq + ' stock last month')
    p = self.makeResponse(safe_query,'plaintext','Result')
    result = urllib.urlopen(p).read()
    dom = minidom.parseString(result)
    x = dom.getElementsByTagName('plaintext')
    if len(x) > 0:
      return x[0].firstChild.nodeValue
    return None

class LinkedIn():
  LINKEDIN = {
	'GLOBAL_KEY' : 'cqgmvmqtxn3z',
	'GLOBAL_SECRET' :'cQs7wMCRtnoLPZmK',
  }

  def __init__(self,user_key,user_secret):
      self.consumer  = oauth.Consumer(key=self.LINKEDIN['GLOBAL_KEY'],secret=self.LINKEDIN['GLOBAL_SECRET'])
      token = oauth.Token(key=user_key,secret=user_secret)
      self.client = oauth.Client(self.consumer,token)

  people = 'http://api.linkedin.com/v1/people/id='
  
  def getPersonInfo(self,searchParam):
    lId = self.findPerson(searchParam)
    if lId is None:
        return None
    return self.getPerson(lId)

  def findPerson(self,searchParam):
    safe_query = urllib.quote(searchParam)
    url = 'http://api.linkedin.com/v1/people-search?keywords=%s?&sort=distance' % (safe_query)
    resp, content = self.client.request(url)
    dom = minidom.parseString(content)
    x = dom.getElementsByTagName('person')
    if len(x) > 0:
      lid = x[0].getElementsByTagName('id')[0]
      return lid.firstChild.nodeValue
    else:
      return None

  def getPerson(self,lid):
    url = self.people + lid + (':(first-name,last-name,location,industry,'
                                'interests,three-current-positions,three-past-positions,'
                                'educations,picture-url,public-profile-url,relation-to-viewer)?format=json')
    resp,content = self.client.request(url)
    if resp['status'] == '403':
        return None
    return json.loads(content)
class Sentinal():
    
    def __init__(self,linked_key,linked_secret):
        self.lnk = LinkedIn(linked_key,linked_secret)
        self.bing = Bing('api_keys.txt')
        self.yahoo = YahooNews()
        self.sc = StockChecker()
    def createResponse(self,sidebar,person,company):
        news = self.getNews(company)
        personal_info = self.lnk.getPersonInfo(person + ' ' + company)
        return {'sidebar': sidebar,'news': news, 'personal' : personal_info, 'person':person,'company':company}

    def getNews(self,company):
        symbol = self.sc.Check(company)
        if symbol is None:
            news = self.bing.getNewsResults(company,6) 
            twitter = self.bing.getTwitter(company)
            news = {'headline': news,'twitter' : twitter}
            
        else:
            headline_news = self.yahoo.getPublicNews(symbol,'headline',8)
            blog_news = self.yahoo.getPublicNews(symbol,'blog',3)
            stock_price = self.sc.Price(symbol)
            more_url = 'http://finance.yahoo.com/q?s=%s' % (symbol)
            stock_graph = ('http://chart.finance.yahoo.com/t?s=%s&'
                             'lang=en-US&region=US&width=350&height=180') % (symbol)
            news = {'symbol' : symbol, 'headline' : headline_news, 'industry' : industry_news,
                    'blog': blog_news, 'more': more_url, 'graph':stock_graph, 'price' : stock_price}
        return news



