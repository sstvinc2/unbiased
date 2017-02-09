from get_sources import *

nyt=get_nyt()
#fox=get_fox()
#nbc=get_nbc()

url=nyt['h2']['href'][0]
print(url)
card=getTwitterCard("https://www.nytimes.com/2017/01/30/us/politics/trump-immigration-ban-memo.html")
#print(card)
