#!/usr/bin/env python
# Madhav Suresh 2011

import urllib


class PackedUrl():
  ''' Request object that is sent to Alchemy API, not all calls
  are supported right now, only the subset we need '''
  _api_key = ''
  _query = ''
  _sources = ''
  
  def __init__(self,api,txt,sources):
    
    self._api_key = api
    self._query = txt
    self._sources = sources

  def getUrl(self,endpoint):
    endpoint = endpoint + '?Appid=' + self._api_key + '&query=' + self._query + '&sources=' + self._sources
    print endpoint
    return endpoint

class Bing():
  _api_key = ''
  _endpoint = 'http://api.search.live.net/json.aspx'



  def readAPIKey(self,fileName):
    f = open(fileName,'r')
    line = f.read().strip()
    x = dict(kvp.split('=') for kvp in line.split(';'))
    self._api_key = x['bing']
    print self._api_key

  def getAPIKey(self):
    return self._api_key

  def getNewsResults(self,txt_req):
    p = PackedUrl(self._api_key,txt_req,'news')
    result = urllib.urlopen(p.getUrl(self._endpoint)).read()
    return result

    
