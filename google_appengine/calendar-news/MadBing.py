#!/usr/bin/env python
# Madhav Suresh 2011

import urllib
from xml.dom import minidom

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
    print self._api_key

  def getNewsResults(self,txtReq,count):
    p = self.makeResponse(txtReq,'news',count)
    result = urllib.urlopen(p).read()
    return result

  def getWebResults(self,txtReq,count):
    p = self.makeResponse(txtReq,'web',count)
    result = urllib.urlopen(p).read()
    return result

class WolframAlpha():
  ''' Request object that is sent to Bing API, not all calls
  are supported right now, only the subset we need '''
  _api_key = ''
  _endpoint = 'http://api.wolframalpha.com/v2/query?'
#


  def __init__(self,api_path):
    self.readAPIKey(api_path)

  def makeResponse(self,txtReq,reqType):
    return self._endpoint + \
	   'appid=' + self._api_key + \
	   '&input=' + txtReq + \
	   '&format=' + reqType + \
           '&includepodid=DateRangeSpecified:Close:FinancialData'

  def readAPIKey(self,fileName):
    f = open(fileName,'r')
    line = f.read().strip()
    x = dict(kvp.split('=') for kvp in line.split(';'))
    self._api_key = x['wolframalpha']

  def getStockResult(self,txtReq):
    p = self.makeResponse(txtReq + 'stock last week','image,plaintext')
    result = urllib.urlopen(p).read()
    dom = minidom.parseString(result)
    x = dom.getElementsByTagName('img')[0]
    return x.getAttribute('src')
