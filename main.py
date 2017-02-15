#!/usr/bin/env python3

from unbiasedObjects import *
from unbiasedFunctions import *
from parser import *
import time

def main():
    while True:
        print('-----------------------')
        run()
        print('-----------------------')
        time.sleep(600)

def run():
    sourceList=[]

    bbc=buildBBC()
    sourceList.append(bbc)

    
    sourceList.append(NewsSource('NBC News',
                                 'http://nbcnews.com',
                                 ['top-stories-section', 'panel_hero', '<a href="'],
                                 ['<div class="story-link', '<a href="'],
                                 [],
                                 None, None,
                                 'ad-content ad-xs mobilebox1', 'taboola-native-top-stories-thumbnail',
                                 None, None))


    sourceList.append(NewsSource('CBS News',
                                 'http://cbsnews.com',
                                 ['<h1 class="title">', '<a href="'],
                                 ['<li data-tb-region-item>', '<a href="'],
                                 [],
                                 None, None, #'Big News Area Side Assets', '</a>'
                                 'Big News Area Side Assets', '</ul></div>',
                                 None, None))


    
    sourceList.append(NewsSource('The Blaze',
                                 'http://theblaze.com',
                                 ['<a class="gallery-link" href="'],
                                 ['</figure>\n\n<figure class="gallery-item">', 'href="'],
                                 [],
                                 '<!-- home -->', '<!-- loop-home -->',
                                 '<!-- home -->', '<!-- loop-home -->',
                                 None, None))
    

    wkl=buildWeeklyStandard()
    sourceList.append(wkl)

    nyt=buildNYT()
    sourceList.append(nyt)

    fox=buildFoxNews()
    sourceList.append(fox)
    
    #scrape all urls and build data structure
    newsSourceArr=buildNewsSourceArr(sourceList)

    #build the output file HTML
    outputHTML=buildOutput(newsSourceArr)
    #print the output file HTML
    printOutputHTML(outputHTML, '/var/www/html/index.html')


if __name__=="__main__":
    main()
