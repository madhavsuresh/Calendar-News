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
   self._api_key = f.readline().strip()

  def getAPIKey(self):
    return self._api_key

  def getRankedTxtEntities(self,request):
    uri = self._endpoint + 'text/TextGetRankedNamedEntities'
    result = urllib.urlopen(uri,request.getParams()).read()
    return result

    
