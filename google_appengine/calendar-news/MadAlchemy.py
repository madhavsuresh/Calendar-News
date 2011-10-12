#!/usr/bin/env python
# Madhav Suresh 2011

import urllib


class PackedRequest():
  ''' Request object that is sent to Alchemy API, not all calls
  are supported right now, only the subset we need '''
  _api_key = ''
  _text = ''
  _outputMode = ''
  
  def __init__(self,api,txt,output):
    
    self._api_key = api
    self._text = txt
    self._outputMode = output

  def getParams(self):
    params = urllib.urlencode({
	    'apikey':self._api_key,
	    'text':self._text,
	    'outputMode':self._outputMode,
    })
    return params

class Alchemy():
  _api_key = ''
  _endpoint = 'http://access.alchemyapi.com/calls/'


  def readAPIKey(self,fileName):
    f = open(fileName,'r')
    line = f.read().strip()
    x = dict(kvp.split('=') for kvp in line.split(';'))
    self._api_key = x['alchemyapi']
    print self._api_key

  def getAPIKey(self):
    return self._api_key

  def getRankedTxtEntities(self,request):
    uri = self._endpoint + 'text/TextGetRankedNamedEntities'
    p = PackedRequest(self._api_key,request,'json')
    result = urllib.urlopen(uri,p.getParams()).read()
    return result

    
