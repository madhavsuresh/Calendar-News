from mad.MadBing import WolframAlpha,Bing,StockChecker,LinkedIn
import simplejson as json
from collections import defaultdict


def multidict(ordered_pairs):
    """Convert duplicate keys values to lists."""
    # read all values into lists
    d = defaultdict(list)
    for k, v in ordered_pairs:
        d[k].append(v)

    # unpack lists that have only 1 item
    for k, v in d.items():
        if len(v) == 1:
            d[k] = v[0]
    return dict(d)



w = WolframAlpha('api_keys.txt')
b = Bing('api_keys.txt')
#print b.getNewsResults('microsoft',3)
#s = StockChecker()
#print s.Check('costco wholesale') #w = WolframAlpha('api_keys.txt')
#x = w.getStockResult("google")
x = w.getStockPrice("google")
print x
#x = w.getNumEmployees("GOOG")
#print x
l = LinkedIn()
print l.getPersonInfo('Jeremy Gilbert')
#x = json.loads(b.getNewsResults("Google",3))
#print x['SearchResponse']['News']['Results']
#print x
#l.getPerson(l.findPerson('Vibhav Sreekanti Maginatics'))
#print b
#txt = b.getRankedTxtEntities('Proctor and Gamble')

server = 'http://api.wolframalpha.com/v2/query?'
appid = '5TV6XG-297R536AJ4'
input = 'who are you?'

