from bs4 import BeautifulSoup
import wget
import os

def getHeds(heds, h_class=None):
    hed_text=[]
    hed_hrefs=[]
    #print(heds[0])
    for hed in heds:
        #print('*'+hed.string)
        if hed.a:
            try:
                if h_class==None or hed['class'][0]==h_class:
                    if hed.a.string!=None: hed_text.append(hed.a.string.strip())
                    if hed.a['href']!='': hed_hrefs.append(hed.a['href'])
            except:
                continue
    return hed_text, hed_hrefs



def get_nyt():
    #init vars
    stories={}

    #download and soup web page
    wget.download('https://nytimes.com', out="nyt.html")
    soup = BeautifulSoup(open("nyt.html", encoding="utf8"), "lxml")
    os.remove('nyt.html')

    #get top story
    h1s=soup('h1')
    h1_heds, h1_href = getHeds(h1s, 'story-heading')
    stories['h1']={'heds':[h1_heds[0]], 'href':[h1_href[0]]}

    #get secondary stories
    aCol = soup.find_all('div', 'a-column')
    h2s=aCol[0].find_all('h2')
    h2_heds, h2_href = getHeds(h2s, 'story-heading')
    stories['h2']={'heds':h2_heds, 'href':h2_href}

    #get tertiary stories
    bCol = soup.find_all('div', 'b-column')
    h3s=bCol[0].find_all('h2')
    h3_heds, h3_href = getHeds(h3s, 'story-heading')
    stories['h3']={'heds':h3_heds, 'href':h3_href}

    return stories


def get_fox():
    #init vars
    stories={}
    h2_heds = []
    h2_href = []

    #download and soup web page
    wget.download('http://www.foxnews.com', out="fox.html")
    soup = BeautifulSoup(open("fox.html", encoding="utf8"), "lxml")
    os.remove('fox.html')

    #get top story
    h1s=soup('h1')
    h1_heds, h1_href = getHeds(h1s)
    stories['h1']={'heds':[h1_heds[0]], 'href':[h1_href[0]]}

    #get secondary stories - <div top-stories><li> (loop for first <a>)
    topStories = soup('div', 'top-stories')
    topStoriesCols = topStories[0].ul
    for c in topStoriesCols.children:
        if c.string==None:
            h2_heds.append(c.h3.text)
            h2_href.append(c.a['href'])

    stories['h2']={'heds':h2_heds, 'href':h2_href}

    #get tertiary stories
    h3s=topStoriesCols.find_all('li')
    h3_heds, h3_href=getHeds(h3s)
    for href in h3_href:
        if href in h2_href:
            h3_href.remove(href)

    stories['h3']={'heds':h3_heds, 'href':h3_href}

    return stories


def get_nbc():
    #init vars
    stories={}

    #download and soup web page
    wget.download('http://www.nbcnews.com', out="nbc.html")
    soup = BeautifulSoup(open("nbc.html", encoding="utf8"), "lxml")
    os.remove('nbc.html')

    #get top story
    panel = soup.find_all('div', 'panel-txt_hero')
    h1_heds=panel[0].find_all('h3')
    panel = soup.find_all('div', 'panel-txt')
    stories['h1']={'heds':[h1_heds[0].text.strip()], 'href':['http://www.nbcnews.com'+panel[0].a['href']]}

    #get secondary stories - div class panel
    h2s = soup.find_all('div', 'story-link_default-height')
    story_heds=[]
    for item in h2s:
        story_heds.append(item.h3.text.strip())
    h2_heds, h2_href = getHeds(h2s)
    for i in range(len(h2_href)):
        h2_href[i]='http://www.nbcnews.com'+h2_href[i]
    stories['h2']={'heds':story_heds[:3], 'href':h2_href[:3]}

    #get tertiary stories - div class story-link
    stories['h3']={'heds':story_heds[3:], 'href':h2_href[3:]}

    return stories

def getTwitterCard(url):
    card={}

    #wget.download(url, out="card.html")
    cmd='wget --no-check-certificate '+url+' -O card.html'
    print(cmd)
    ret=os.system(cmd)
    print(ret)
    soup = BeautifulSoup(open("card.html", encoding="utf8"), "lxml")
    #os.remove('card.html')

    hed=soup.find_all('meta', {'name' : 'twitter:title'})
    card['hed']=hed[0]['content']

    img=soup.find_all('meta', {'name' : 'twitter:image'})
    card['img']=img[0]['content']

    return card



'''  
links=get_nbc()
card=getTwitterCard(links['h2']['href'][0])
print(card)


nyt=get_nyt()
fox=get_fox()
nbc=get_nbc()
'''
