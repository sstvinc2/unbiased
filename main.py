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

    nbc=buildNBC()
    sourceList.append(nbc)

    cbs=buildCBS()
    sourceList.append(cbs)

    
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
