#!/usr/bin/env python
# Madhav Suresh 2011

import urllib


class PackedRequest():
  ''' Request object that is sent to Alchemy API, not all calls
  are supported right now, only the subset we need '''
  _api_key = ''
  _text = ''
  _outputMode = ''

  pass
  
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


  def __init__(self,api_path):
    self.readAPIKey(api_path)

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

def multidict(ordered_pairs):
    """convert duplicate keys values to lists."""
    # read all values into lists
    d = defaultdict(list)
    for k, v in ordered_pairs:
        d[k].append(v)

    # unpack lists that have only 1 item
    for k, v in d.items():
        if len(v) == 1:
            d[k] = v[0]
    return dict(d)


    
