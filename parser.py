#!/usr/bin/env python3

from unbiasedObjects import *
from unbiasedFunctions import buildArticle
import os

def buildNYT():
    url='http://www.nytimes.com'

    #download file
    os.system('wget -q -O scratch/temp1.html --no-check-certificate '+url)
    
    #read file
    f=open('scratch/temp1.html', 'r')#, encoding="utf8")
    content=f.read()
    f.close()

    #get main headline
    #this will likely need if/else logic
    h1=content

    #This is with a large headline over a and b columns
    h1=h1.split('story theme-summary banner', 1)[1]
    h1=h1.split('<a href="', 1)[1]
    h1=h1.split('"', 1)[0]

    #GET SECONARY HEADLINES
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

    #REMOVE DUPLICATES
    removeArr=[]
    for i in range(len(h2s)):
        for j in range(len(h2s)):
            if i==j:
                continue
            else:
                if h2s[i] in h2s[j]:
                    removeArr.append(h2s[j])
    for x in removeArr:
        h2s.remove(x)


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
    #REMOVE DUPLICATES
    removeArr=[]
    for i in range(len(h3s)):
        for j in range(len(h3s)):
            if i==j:
                continue
            else:
                if h3s[i] in h3s[j]:
                    removeArr.append(h3s[j])
    for x in removeArr:
        h3s.remove(x)


    #BUILD THE ARTICLES BASED ON URLS
    h1Arr=[]
    h1Arr.append(buildArticle(h1, 'New York Times'))

    h2Arr=[]
    for x in h2s:
        h2Arr.append(buildArticle(x, 'New York Times'))

    h3Arr=[]
    for x in h3s:
        h3Arr.append(buildArticle(x, 'New York Times'))

    nyt=NewsSource2('New York Times', 'http://nytimes.com', h1Arr, h2Arr, h3Arr)

    return nyt




'''
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
