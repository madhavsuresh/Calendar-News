from mad.MadBing import LinkedIn,Sentinal,StockChecker,Bing
llk = 'b398af13-cc5e-4bcf-ab3a-e97cb0aa1226'
lk = '07e2b29b-2a6b-4708-89bb-0e9c94992af2'
LINKEDIN_KEY		=  "cqgmvmqtxn3z"
LINKEDIN_SECRET		=  "cQs7wMCRtnoLPZmK"
l = LinkedIn(llk,lk)
#x = l.findPerson('Nick Merril')
#print l.getPerson(l.findPerson('Vibhav Sreekanti Riverbed'))
#x =StockChecker()
#print x.Price('goog')
b = Bing('api_keys.txt')
#print b.getNewsResults('Google',6)
print b.getTwitter('aerofs')
#s = Sentinal(llk,lk)
#print s.createResponse([],'Vibhav Sreekanti', 'Google')
