#!/usr/bin/env python3

import logging
import os
import re
import urllib.parse

from bs4 import BeautifulSoup
import requests

from unbiased.unbiasedObjects import *
from unbiased.unbiasedFunctions import buildArticle

logger = logging.getLogger('unbiased')


'''
Takes in a URL, downloads the file to a temp file,
reads the file into a string, and returns that string
'''
def urlToContent(url, sourceEncoding='utf8'):
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    else:
        raise Exception("Failed to download {}".format(url))


'''
Creates a new newsSource2 object. For each URL in h1-h3URLs,
calls the file scraper and appends the new Article object.
Returns a newsSource2 object
'''
def buildNewsSource2(name, url, h1URLs, h2URLs, h3URLs):

    url_parts = urllib.parse.urlparse(url)
    scheme = url_parts.scheme
    h1URLs = [urllib.parse.urlparse(x, scheme=scheme).geturl() for x in h1URLs]
    h2URLs = [urllib.parse.urlparse(x, scheme=scheme).geturl() for x in h2URLs]
    h3URLs = [urllib.parse.urlparse(x, scheme=scheme).geturl() for x in h3URLs]

    h1Arr=[]
    a=buildArticle(h1URLs[0], name)
    if a==None:
        logger.debug('H1 Nonetype in '+name)
    else:
        h1Arr.append(a)

    h2Arr=[]
    for x in h2URLs:
        a=buildArticle(x, name)
        if a!=None:
            h2Arr.append(a)
        else:
            logger.debug('H2 Nonetype in '+name)

    h3Arr=[]
    for x in h3URLs:
        a=buildArticle(x, name)
        if a!=None:
            h3Arr.append(a)
        else:
            logger.debug('H3 Nonetype in '+name)

    #BUILD THE NEWS SOURCE
    newsSource=NewsSource2(name, url, h1Arr, h2Arr, h3Arr)

    return newsSource


'''
Some sites will replicate URLs across the page. This function removes them.
Check hierarchically: if h3 exists in h1s or h2s, remove from h3s;
if h2 exists in h1s, remove from h2s

also check partial URLs (e.g. nytimes.com/story.html is the same as
nytimes.com/story.html?var=x
'''
def removeDuplicates(h1s, h2s, h3s):
    #Assume h1s is one element, and keep it

    #remove h2 duplicates
    removeArr=[]
    for i in range(len(h2s)):
        #check internally
        for j in range(len(h2s)):
            if i==j:
                continue
            else:
                if h2s[i] in h2s[j]:
                    removeArr.append(h2s[j])
        #check against h1s
        for k in range(len(h1s)):
            if (h2s[i] in h1s[k]) or (h1s[k] in h2s[i]):
                removeArr.append(h2s[i])
    for x in removeArr:
        h2s.remove(x)
    
    #remove h3 duplicates
    removeArr=[]
    for i in range(len(h3s)):
        #check internally
        for j in range(len(h3s)):
            if i==j:
                continue
            else:
                if h3s[i] in h3s[j]:
                    removeArr.append(h3s[j])
        #check against h1s and h2s
        h1and2=h1s+h2s
        for k in range(len(h1and2)):
            if (h3s[i] in h1and2[k]) or (h1and2[k] in h3s[i]):
                removeArr.append(h3s[i])
    for x in removeArr:
        if x in h3s:
            h3s.remove(x)
    

    return h1s, h2s, h3s



def removalNotification(source, title, reason, value):
    logger.debug("""Story removed
    SOURCE:\t{}
    TITLE:\t{})
    REASON:\t{}
    VALUE:\t{}""".format(source, title, reason, value))


def removeBadStoriesHelper(source, element, badStringList, article_tiers):
    if badStringList is None:
        return
    for tier, articles in enumerate(article_tiers):
        print(tier, articles)
        for idx, article in enumerate(articles):
            print(article)
            if article is None:
                logger.debug("None type found in removeBadStoriesHelper for {}".format(source.name))
                break
            for item in badStringList:
                if item in getattr(article, element):
                    article_tiers[tier].remove(article)
                    # if it's in the h1 slot, bump up the
                    # first h2 into the h1 slot
                    if tier == 0 and len(article_tiers[1]) > 0:
                        article_tiers[0].append(article_tiers[1][0])
                        article_tiers[1].remove(article_tiers[1][0])
                    removalNotification(source.name, article.title, element, item)


def removeBadStories(source, badTitleArr, badDescArr, badAuthorArr, badImgArr, badURLArr=None):

    arr=[source.h1Arr, source.h2Arr, source.h3Arr]

    removeBadStoriesHelper(source, "title", badTitleArr, arr)
    removeBadStoriesHelper(source, "description", badDescArr, arr)
    removeBadStoriesHelper(source, "author", badAuthorArr, arr)
    removeBadStoriesHelper(source, "img", badImgArr, arr)
    removeBadStoriesHelper(source, "url", badURLArr, arr)
                    
    return source




def buildTheHill():
    url='http://thehill.com'
    name='The Hill'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    h1=content
    h1=h1.split('<div class="headline-story-image">', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=[url+h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('<div class="section-top-content">', 1)[1]
    h2=h2.split('</ul>', 1)[0]
    while '<div class="top-story-item' in h2 and len(h2s)<4:
        h2=h2.split('<div class="top-story-item', 1)[1]
        x=h2.split('<a href="', 1)[1]
        x=x.split('"', 1)[0]
        h2s.append(url+x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('<div class="section-top-content">', 1)[1]
    h3=h3.split('</ul>', 1)[0]
    while '<div class="top-story-item small' in h3:
        h3=h3.split('<div class="top-story-item small', 1)[1]
        x=h3.split('<a href="', 1)[1]
        x=x.split('"', 1)[0]
        h3s.append(url+x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    hil=buildNewsSource2(name, url, h1s, h2s, h3s)
    hil=removeBadStories(hil, ['THE MEMO'], None, ['Matt Schlapp', 'Juan Williams', 'Judd Gregg'], None, None)

    return hil





def buildGuardian():
    url='http://www.theguardian.com/us'
    name='The Guardian US'


    while True:
        #DOWNLOAD HOMEPAGE CONTENT
        content=urlToContent(url, 'utf8')
        
        #get main headline
        h1=content
        h1=h1.split('<h1', 1)[1]
        h1=h1.split('<a href="', 1)[1]
        h1=h1.split('"', 1)[0]

        if h1!='https://www.theguardian.com/us':
            break
        else:
            logger.debug('Guardian loop')
        
    h1s=[h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    #only the h1 and the two h2s have this, so split on it and grab
    #the second two
    h2=h2.split('<div class="fc-item__image-container u-responsive-ratio inlined-image">')[2:]
    for x in h2:
        if '<h2 class="fc-item__title"><a href="' in x:
            x=x.split('<h2 class="fc-item__title"><a href="', 1)[1]
            x=x.split('"', 1)[0]
            h2s.append(x)
        else:
            break

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('<div class="fc-slice-wrapper">', 1)[1]
    h3=h3.split('<div class="fc-container__inner">', 1)[0]#'<div class="js-show-more-placeholder">', 1)[0]
    #this story section goes on forever; just grab the first 5
    while '<h2 class="fc-item__title"><a href="' in h3:
        h3=h3.split('<h2 class="fc-item__title"><a href="', 1)[1]
        x=h3.split('"', 1)[0]
        h3s.append(x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    
    gdn=buildNewsSource2(name, url, h1s, h2s, h3s)
    gdn=removeBadStories(gdn, None, ['Tom McCarthy', 'Andy Hunter'], ['https://www.theguardian.com/profile/ben-jacobs'], None)

    return gdn



def buildWashTimes():
    url='http://www.washingtontimes.com/'
    name='Washington Times'


    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)
    
    #get main headline
    h1=content
    h1=h1.split('top-news', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]

    h1s=[url+h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('class="top-news', 1)[1]
    h2=h2.split('</article>', 1)[1] #end of top-news article
    h2=h2.split('<article ', 1)[0] #note the space; we want unclassed articles
    h2=h2.split('<article>')[1:]
    
    for x in h2:
        x=x.split('<a href="', 1)[1]
        x=x.split('"', 1)[0]
        h2s.append(url+x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('more-from desktop-only', 1)[1]
    h3=h3.split('</section>', 1)[0]
    h3=h3.split('<a href="')[1:]
    
    for x in h3:
        x=x.split('"', 1)[0]
        h3s.append(url+x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)

    wat=buildNewsSource2(name, url, h1s, h2s, h3s)
    wat=removeBadStories(wat, None, None, None, None)

    return wat


def buildCSM():
    url='http://www.csmonitor.com/USA'
    name='Christian Science Monitor'


    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #this makes sure we don't get '/USA' in the URL twice
    url=url.split('/USA')[0]
    
    #get main headline
    h1=content
    h1=h1.split('block-0-0', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]

    h1s=[url+h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('block-1-0', 1)[1]
    h2=h2.split('ui-section-middle', 1)[0]
    h2=h2.split('<h3 class="story_headline">')[1:]
    
    for x in h2:
        temp=x.split('<a href="', 2)[1:]
        x=temp[0]
        x=x.split('"', 1)[0]
        if x=='/csmlists/special/first-look':
            x=temp[1]
            x=x.split('"', 1)[0]

        h2s.append(url+x)
    #also add in the floating story on the left
    h2=content
    h2=h2.split('block-0-1', 1)[1]
    h2=h2.split('<h3 class="story_headline">')[1]
    h2=h2.split('<a href="', 2)[2]
    h2=h2.split('"', 1)[0]
    h2s.append(url+h2)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('block-0-2', 1)[1]
    h3=h3.split('ui-section-top-right', 1)[0]
    h3=h3.split('<h3 class="story_headline')[1:]
    
    for x in h3:
        x=x.split('<a href="', 2)[-1]
        x=x.split('"', 1)[0]
        h3s.append(url+x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)

    csm=buildNewsSource2(name, url, h1s, h2s, h3s)

    badTitleArr=['Change Agent']
    badDescArr=None
    badAuthorArr=None
    badImgArr=['csm_logo']
    badURLArr=['difference-maker']
    csm=removeBadStories(csm, badTitleArr, badDescArr, badAuthorArr, badImgArr, badURLArr)

    return csm



'''
Function to fix the oddly short og:descriptions provided
in The Blaze articles by grabbing the first portion of the story instead
'''
def blazeFixDesc(articleArr):
    TAG_RE = re.compile(r'<[^>]+>')
    for i in range(len(articleArr)):
        desc=urlToContent(articleArr[i].url)
        desc=desc.split('<div class="entry-content article-styles">', 1)[1]
        desc=desc.split('<p>', 1)[1]
        desc=TAG_RE.sub('', desc)
        desc=desc.replace('\n', ' ')
        desc=desc[:144]
        articleArr[i].description=desc

    return articleArr
    


def buildBlaze():
    url='http://theblaze.com'
    name='The Blaze'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    h1=content
    h1=h1.split('<!-- home -->', 1)[1]
    h1=h1.split('<a class="gallery-link" href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=[url+h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('<!-- home -->', 1)[1]
    h2=h2.split('<!-- loop-home -->', 1)[0]
    while '<a class="gallery-link" href="' in h2:#'</figure>\n\n<figure class="gallery-item">' in h2:
        h2=h2.split('<a class="gallery-link" href="', 1)[1]#'</figure>\n\n<figure class="gallery-item">', 1)[1]
        #h2=h2.split('href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append(url+x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('<!-- loop-home -->', 1)[1]
    #this story section goes on forever; just grab the first 5
    while len(h3s)<5:
        h3=h3.split('<a class="feed-link" href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append(url+x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)

    blz=buildNewsSource2(name, url, h1s, h2s, h3s)

    badTitleArr=['Tucker Carlson', 'Mark Levin']
    badDescArr=['Lawrence Jones', 'Mike Slater']
    badAuthorArr=['Matt Walsh', 'Tomi Lahren', 'Dana Loesch', 'Mike Opelka', 'Chris Salcedo', 'Justin Haskins', 'Sara Gonzales', 'Doc Thompson', 'Glenn Beck']
    badImgArr=None
    badURLArr=None
    blz=removeBadStories(blz, badTitleArr, badDescArr, badAuthorArr, badImgArr, badURLArr)

    
    #The Blaze has dumb, short description fields, so we need to grab
    #the first x characters of actual article text instead
    blz.h1Arr=blazeFixDesc(blz.h1Arr)
    blz.h2Arr=blazeFixDesc(blz.h2Arr)
    blz.h3Arr=blazeFixDesc(blz.h3Arr)

    return blz



def buildCBS():
    url='http://cbsnews.com'
    name='CBS News'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    h1=content
    if '<h1 class="title">' in content:
        h1=h1.split('<h1 class="title">', 1)[1]
        h1=h1.split('<a href="', 1)[1]
        h1=h1.split('"', 1)[0]
        h1s=[url+h1]
    else:
        #for cases where they lead with a video, pull the first h2 as h1
        h1=h1.split('Big News Area Side Assets', 1)[1]
        h1=h1.split('</ul></div>', 1)[0]
        h1=h1.split('<li data-tb-region-item>', 1)[1]
        h1=h1.split('<a href="', 1)[1]
        x=h1.split('"', 1)[0]
        h1s=[url+x]
        

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('Big News Area Side Assets', 1)[1]
    h2=h2.split('</ul></div>', 1)[0]
    while '<li data-tb-region-item>' in h2:
        h2=h2.split('<li data-tb-region-item>', 1)[1]
        h2=h2.split('<a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append(url+x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('Latest News', 1)[1]
    #this story section goes on forever; just grab the first 5
    while len(h3s)<5:
        h3=h3.split('<li class="item-full-lead"', 1)[1]
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append(url+x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    cbs=buildNewsSource2(name, url, h1s, h2s, h3s)
    cbs=removeBadStories(cbs, ['60 Minutes'], ['60 Minutes'], None, None, ['whats-in-the-news-coverart'])

    return cbs





def buildNBC():    
    url='http://nbcnews.com'
    name='NBC News'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    h1=content
    h1=h1.split('top-stories-section', 1)[1]
    h1=h1.split('panel_hero', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]
    if '.com' not in h1:
        h1=url+h1
    h1s=[h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('ad-content ad-xs mobilebox1', 1)[1]
    h2=h2.split('taboola-native-top-stories-thumbnail', 1)[0]
    while '<div class="story-link' in h2:
        h2=h2.split('<div class="story-link', 1)[1]
        h2=h2.split('<a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            if '.com' not in x:
                x=url+x
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('js-more-topstories', 1)[1]
    h3=h3.split('<div class="panel-section', 1)[0]
    while '<div class="story-link' in h3:
        h3=h3.split('<div class="story-link', 1)[1]
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            if '.com' not in x:
                x=url+x
            h3s.append(x)

    #adjust for today.com urls
    '''
    for arr in [h1s, h2s, h3s]:
        for i in range(len(arr)):
            if 'today.com' in arr[i]:
                arr[i]=arr[i].split('.com', 1)[1]
    '''

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    nbc=buildNewsSource2(name, url, h1s, h2s, h3s)
    nbc=removeBadStories(nbc, None, ['First Read'], None, None, None)


    return nbc




def buildBBC():    
    url='http://www.bbc.com/news/world/us_and_canada'
    name='BBC US & Canada'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    h1=content
    h1=h1.split('buzzard-item', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=['http://www.bbc.com'+h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('<div class="pigeon">', 1)[1]
    h2=h2.split('<div id=', 1)[0]
    while 'top_stories#' in h2:
        h2=h2.split('top_stories#', 1)[1]
        h2=h2.split('<a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append('http://www.bbc.com'+x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('<div class="macaw">', 1)[1]
    h3=h3.split('Watch/Listen', 1)[0]
    while '<div class="macaw-item' in h3:
        h3=h3.split('<div class="macaw-item', 1)[1]
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append('http://www.bbc.com'+x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    bbc=buildNewsSource2(name, url, h1s, h2s, h3s)
    badTitleArr=None
    badDescArr=None
    badAuthorArr=None
    badImgArr=['bbc_news_logo.png']
    bbc=removeBadStories(bbc, badTitleArr, badDescArr, badAuthorArr, badImgArr)

    
    #REMOVE ' - BBC News' from headlines
    for i in range(len(bbc.h1Arr)):
        if ' - BBC News' in bbc.h1Arr[i].title:
            bbc.h1Arr[i].title=bbc.h1Arr[i].title.split(' - BBC News', 1)[0]
    for i in range(len(bbc.h2Arr)):
        if ' - BBC News' in bbc.h2Arr[i].title:
            bbc.h2Arr[i].title=bbc.h2Arr[i].title.split(' - BBC News', 1)[0]
    for i in range(len(bbc.h3Arr)):
        if ' - BBC News' in bbc.h3Arr[i].title:
            bbc.h3Arr[i].title=bbc.h3Arr[i].title.split(' - BBC News', 1)[0]

    return bbc



def buildWeeklyStandard():
    url='http://www.weeklystandard.com'
    name='Weekly Standard'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)
    
    #get main headline
    h1=content
    h1=h1.split('<div id="region_1"', 1)[1]
    h1=h1.split('<div id="region_2"', 1)[0]
    h1=h1.split('<div class="lead-photo">', 1)[1]
    h1=h1.split('href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=[h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('<div class="widget lead-story layout-3col-feature" data-count="2">', 1)[1]
    h2=h2.split('<div id="region_2"', 1)[0]
    while '<div class="lead-photo">' in h2:
        h2=h2.split('<div class="lead-photo">', 1)[1]
        h2=h2.split('href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('Today\'s Standard', 1)[1]
    h3=h3.split('<div id="region_3"', 1)[0]
    while '<div class="lead-photo">' in h3:
        h3=h3.split('<div class="lead-photo">', 1)[1]
        h3=h3.split('href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append(x)

    #Need to add URL prefix to all URLs
    for i in range(len(h1s)):
        h1s[i]=url+h1s[i]
    for i in range(len(h2s)):
        h2s[i]=url+h2s[i]
    for i in range(len(h3s)):
        h3s[i]=url+h3s[i]
        

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    wkl=buildNewsSource2(name, url, h1s, h2s, h3s)

    #REMOVE BAD STORIES
    badTitleArr=None
    ## if flagged again, remove Micah Mattix
    badDescArr=['Matt Labash']
    badAuthorArr=['MATT LABASH', 'TWS PODCAST', 'ERIC FELTEN', 'Steven J. Lenzner', 'MARK HEMINGWAY']
    badImgArr=['http://www.weeklystandard.com/s3/tws15/images/twitter/tws-twitter_1024x512.png']
    wkl=removeBadStories(wkl, badTitleArr, badDescArr, badAuthorArr, badImgArr)

    return wkl




def buildNPR():
    url='http://www.npr.org/sections/news/'
    name='NPR'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)
    
    #get main headline
    h1=content
    h1=h1.split('<a id="mainContent">', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=[h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('<article class="item has-image">', 1)[1]
    h2=h2.split('<!-- END CLASS=\'FEATURED-3-UP\' -->', 1)[0]
    while '<article class="item has-image">' in h2:
        h2=h2.split('<article class="item has-image">', 1)[1]
        h2=h2.split('<a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('<div id="overflow" class="list-overflow"', 1)[1]
    h3=h3.split('<!-- END ID="OVERFLOW" CLASS="LIST-OVERFLOW"', 1)[0]
    while '<h2 class="title"><a href="' in h3:
        h3=h3.split('<h2 class="title"><a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append(x)

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)

    npr=buildNewsSource2(name, url, h1s, h2s, h3s)

    #REMOVE BAD STORIES
    badTitleArr=['The Two-Way']
    badDescArr=None
    badAuthorArr=['Domenico Montanaro']
    badImgArr=None
    npr=removeBadStories(npr, badTitleArr, badDescArr, badAuthorArr, badImgArr)

    return npr





def buildABC():
    url='http://www.abcnews.go.com'
    name='ABC News'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)
    
    #get main headline
    h1=content
    h1=h1.split('id="row-1"', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=[h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('id="row-2"', 1)[1]
    h2=h2.split('id="row-3"', 1)[0]
    h2=h2.split('card single row-item')[1:3] #should just be 2 of these
    for x in h2:
        x=x.split('<a href="', 1)[1]
        x=x.split('"', 1)[0]
        if h1 not in x:
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('id="row-1"', 1)[1]
    h3=h3.split('tab-data active', 1)[1]
    h3=h3.split('tab-data"', 1)[0] #note the trailing quotation
    while '<a href="' in h3:
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append(x)

    h1s, h2s, h3s = removeDuplicates([h1], h2s, h3s)
    abc=buildNewsSource2(name, url, h1s, h2s, h3s)

    #REMOVE BAD STORIES
    badTitleArr=None
    badDescArr=None
    badAuthorArr=None
    badImgArr=None
    badURLArr=None
    abc=removeBadStories(abc, badTitleArr, badDescArr, badAuthorArr, badImgArr, badURLArr)

    return abc




def buildFoxNews():
    url = 'http://foxnews.com'
    name = 'Fox News'

    # DOWNLOAD HOMEPAGE CONTENT
    content = urlToContent(url)
    soup = BeautifulSoup(content, 'lxml')

    # get main headline
    h1 = soup.find('div', id='big-top')\
             .find('div', class_='primary')\
             .find('h1')\
             .find('a')
    h1 = h1['href']
    h1s = [h1]
    h1s = ['http:' + x if x.startswith('//') else x for x in h1s]

    #GET SECONDARY HEADLINES
    h2s = soup.find('div', id='big-top').find('div', class_='top-stories').select('li > a')
    h2s = [x['href'] for x in h2s]
    h2s = ['http:' + x if x.startswith('//') else x for x in h2s]

    #GET TERTIARY HEADLINES
    h3s = []
    for ul in soup.find('section', id='latest').find_all('ul', recursive=False):
        for li in ul.find_all('li', recursive=False):
            h3s.append(li.find('a')['href'])
    h3s = ['http:' + x if x.startswith('//') else x for x in h3s]

    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)
    fox=buildNewsSource2(name, url, h1s, h2s, h3s)

    #REMOVE BAD STORIES
    badTitleArr=['O&#039;Reilly', 'Fox News', 'Brett Baier', 'Tucker']
    badDescArr=['Sean Hannity']
    badAuthorArr=['Bill O\'Reilly', 'Sean Hannity', 'Howard Kurtz']
    badImgArr=['http://www.foxnews.com/content/dam/fox-news/logo/og-fn-foxnews.jpg']
    badURLArr=['http://www.foxnews.com/opinion', 'videos.foxnews.com']
    fox=removeBadStories(fox, badTitleArr, badDescArr, badAuthorArr, badImgArr, badURLArr)

    return fox



def buildNYT():
    url='http://www.nytimes.com'
    name='New York Times'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    #this will likely need if/else logic
    h1=content

    if 'story theme-summary banner' in h1:
        #This is with a large headline over a and b columns
        h1=h1.split('story theme-summary banner', 1)[1]
        h1=h1.split('<a href="', 1)[1]
        h1=h1.split('"', 1)[0]
    else:
        #otherwise, pull the first story from the A column
        h1=h1.split('<div class="a-column column">', 1)[1]
        h1=h1.split('<article class="story theme-summary lede"', 1)[1]
        h1=h1.split('<a href="', 1)[1].split('"', 1)[0]
    h1s=[h1]
        

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    #A column
    h2=h2.split('<div class="a-column column">', 1)[1]
    h2=h2.split('<!-- close a-column -->', 1)[0]
    #remove "collection" sets
    while '<div class="collection headlines">' in h2:
        arr=h2.split('<div class="collection headlines">', 1)
        h2=arr[0]+arr[1].split('</ul>', 1)[1]
    #Grab the remaining URLs
    while '<a href="' in h2:
        h2=h2.split('<a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3s=[]
    #B column
    h3=content
    h3=h3.split('<div class="b-column column">', 1)[1]
    h3=h3.split('<!-- close b-column -->', 1)[0]
    #remove "collection" sets
    while '<div class="collection headlines">' in h3:
        arr=h3.split('<div class="collection headlines">', 1)
        h3=arr[0]+arr[1].split('</ul>', 1)[1]
    #Grab the remaining URLs
    while '<a href="' in h3:
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if (h1 not in x) and (x not in h3s):
            h3s.append(x)

    '''
    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    if '<!-- close lede-package-region -->' in h3:
        h3=h3.split('<!-- close lede-package-region -->', 1)[1]
        h3=h3.split('<a href="https://www.nytimes.com/tips">', 1)[0]
    elif '/video/the-daily-360' in h3:
        h3=h3.split('/video/the-daily-360')[-1]
        h3=h3.split('More News', 1)[0]
    #remove "collection" sets
    while '<div class="collection headlines">' in h2:
        arr=h3.split('<div class="collection headlines">', 1)
        h3=arr[0]+arr[1].split('</ul>', 1)[1]
    
    #Grab the remaining URLs
    while '<a href="' in h3:
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if (h1 not in x) and (x not in h3s):
            h3s.append(x)
    '''
            
    h1s, h2s, h3s = removeDuplicates(h1s, h2s, h3s)

    nyt=buildNewsSource2(name, url, h1s, h2s, h3s)
    nyt=removeBadStories(nyt, None, None, None, None, ['https://www.nytimes.com/section/magazine', 'https://www.nytimes.com/newsletters/the-interpreter'])

    
    return nyt




'''
NYT
EXAMPLE OF BIG HEADLINE SPANNING BOTH A AND B COLUMNS

<div class="span-ab-layout layout">

    <div class="ab-column column">

        <section id="top-news" class="top-news">
            <h2 class="section-heading visually-hidden">Top News</h2>

                            <div class="above-banner-region region">

                    <div class="collection">
            <div class="hpHeader" id="top-megapackage-kicker">
  <h6><a href="http://www.nytimes.com/pages/politics/index.html?src=hpHeader">The 45th President</a></h6>
</div>

</div>

                </div><!-- close above-banner-region -->
            
                            <div class="span-ab-top-region region">

                    <div class="collection">
            <article class="story theme-summary banner" id="topnews-100000004932040" data-story-id="100000004932040" data-rank="0" data-collection-renderstyle="Banner">
            <h1 class="story-heading"><a href="https://www.nytimes.com/2017/02/14/us/politics/fbi-interviewed-mike-flynn.html">F.B.I. Questioned Flynn About Russia Call</a></h1>
</article>
</div>

                </div><!-- close span-ab-top-region -->
'''
