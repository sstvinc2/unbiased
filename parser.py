#!/usr/bin/env python3

from unbiasedObjects import *
from unbiasedFunctions import buildArticle
import os


'''
Takes in a URL, downloads the file to a temp file,
reads the file into a string, and returns that string
'''
def urlToContent(url):
    #download file
    os.system('wget -q -O scratch/temp1.html --no-check-certificate '+url)
    
    #read file
    f=open('scratch/temp1.html', 'r')#, encoding="utf8")
    content=f.read()
    f.close()

    return content


'''
Creates a new newsSource2 object. For each URL in h1-h3URLs,
calls the file scraper and appends the new Article object.
Returns a newsSource2 object
'''
def buildNewsSource2(name, url, h1URLs, h2URLs, h3URLs):
    h1Arr=[]
    h1Arr.append(buildArticle(h1URLs[0], name))

    h2Arr=[]
    for x in h2URLs:
        h2Arr.append(buildArticle(x, name))

    h3Arr=[]
    for x in h3URLs:
        h3Arr.append(buildArticle(x, name))

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
        h3s.remove(x)
    

    return h1s, h2s, h3s
    

def buildFoxNews():
    url='http://foxnews.com'
    name='Fox News'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)
    
    #get main headline
    h1=content
    h1=h1.split('<h1><a href="', 1)[1]
    h1=h1.split('"', 1)[0]
    h1s=[h1]

    #GET SECONDARY HEADLINES
    h2=content
    h2s=[]
    h2=h2.split('<div class="top-stories">', 1)[1]
    h2=h2.split('<section id="latest"', 1)[0]
    while '<li data-vr-contentbox=""><a href="' in h2:
        h2=h2.split('<li data-vr-contentbox=""><a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if h1 not in x:
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('div id="big-top"', 1)[1]
    h3=h3.split('<div class="top-stories">', 1)[0]
    while '<a href="' in h3:
        h3=h3.split('<a href="', 1)[1]
        x=h3.split('"', 1)[0]
        if h1 not in x:
            h3s.append(x)

    h1s, h2s, h3s = removeDuplicates([h1], h2s, h3s)
    fox=buildNewsSource2(name, url, h1s, h2s, h3s)

    return fox



def buildNYT():
    url='http://www.nytimes.com'
    name='New York Times'

    #DOWNLOAD HOMEPAGE CONTENT
    content=urlToContent(url)

    #get main headline
    #this will likely need if/else logic
    h1=content

    #This is with a large headline over a and b columns
    h1=h1.split('story theme-summary banner', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]

    #GET SECONDARY HEADLINES
    #This comes from the a column or b column, above the break
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

    #B column
    h2=content
    h2=h2.split('<div class="b-column column">', 1)[1]
    h2=h2.split('<!-- close b-column -->', 1)[0]
    #remove "collection" sets
    while '<div class="collection headlines">' in h2:
        arr=h2.split('<div class="collection headlines">', 1)
        h2=arr[0]+arr[1].split('</ul>', 1)[1]
    #Grab the remaining URLs
    while '<a href="' in h2:
        h2=h2.split('<a href="', 1)[1]
        x=h2.split('"', 1)[0]
        if (h1 not in x) and (x not in h2s):
            h2s.append(x)

    #GET TERTIARY HEADLINES
    h3=content
    h3s=[]
    h3=h3.split('<!-- close lede-package-region -->', 1)[1]
    h3=h3.split('<a href="https://www.nytimes.com/tips">', 1)[0]
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

    h1s, h2s, h3s = removeDuplicates([h1], h2s, h3s)
    nyt=buildNewsSource2(name, url, h1s, h2s, h3s)

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
