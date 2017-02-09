#!/usr/bin/env python3

from unbiasedObjects import *
from unbiasedFunctions import *
import time

def main():
    while True:
        print('-----------------------')
        run()
        print('-----------------------')
        time.sleep(120)

def run():
    sourceList=[]
    sourceList.append(NewsSource('New York Times',
                                 'http://nytimes.com',
                                 ['<a href="'],#'<h1 class="story-heading"><a href="'],#['"b-column column', 'h2 class="story-heading"><a href="'],
                                 ['article class="story theme-summary', 'h2 class="story-heading"><a href="'],
                                 ['<hr class="single-rule"', 'article class="story theme-summary', 'h2 class="story-heading"><a href="'],
                                 '<div class="b-column column">', '<!-- close photo-spot-region -->',
                                 'section id="top-news" class="top-news"', '</div><!-- close a-column -->',
                                 'class="second-column-region region"', 'html.geo-dma-501 .nythpNYRegionPromo'))

    sourceList.append(NewsSource('Fox News',
                                 'http://foxnews.com',
                                 ['<h1><a href="'],
                                 ['<li data-vr-contentbox=""><a href="'],
                                 [],
                                 None, None,
                                 '<div class="top-stories">', '<section id="latest"',
                                 None, None))



    sourceList.append(NewsSource('NBC News',
                                 'http://nbcnews.com',
                                 ['top-stories-section', 'panel_hero', '<a href="'],
                                 ['panel panel_default', '<a href="'],
                                 [],
                                 None, None,
                                 'row_no-clear ad-container ad-container_default ad-hide ad-container-mobilebox1', 'js-more-topstories',
                                 None, None))


    sourceList.append(NewsSource('CBS News',
                                 'http://cbsnews.com',
                                 ['<h1 class="title"><a href="'],
                                 ['<li data-tb-region-item>', '<a href="'],
                                 [],
                                 None, None,
                                 'Big News Area Side Assets', '</ul></div>',
                                 None, None))
    
    #scrape all urls and build data structure
    newsSourceArr=buildNewsSourceArr(sourceList)

    #build the output file HTML
    outputHTML=buildOutput(newsSourceArr)
    #print the output file HTML
    printOutputHTML(outputHTML, '/var/www/html/index.html')#'unbiased.html')


if __name__=="__main__":
    main()
