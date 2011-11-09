from MadBing import WolframAlpha,Bing
import wap
from MadAlchemy import PackedRequest,Alchemy
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
x = w.getStockResult("google")
print x
#txt = b.getRankedTxtEntities('Proctor and Gamble')

server = 'http://api.wolframalpha.com/v2/query?'
appid = '5TV6XG-297R536AJ4'
input = 'who are you?'

