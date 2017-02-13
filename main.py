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


    sourceList.append(NewsSource('BBC US',
                                 'http://www.bbc.com/news/world/us_and_canada',
                                 ['buzzard-item', '<a href="'],
                                 ['top_stories#', '<a href="'],
                                 [],
                                 None, None,
                                 '<div class="pigeon">','<div id=',
                                 None, None,
                                 'http://www.bbc.com'))

    
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
                                 ['<a href="'],
                                 ['<li data-tb-region-item>', '<a href="'],
                                 [],
                                 'Big News Area Side Assets', '</a>'
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
    

    sourceList.append(NewsSource('Weekly Standard',
                                 'http://www.weeklystandard.com/',
                                 ['<div class="lead-photo">', 'href="'],
                                 ['<div class="lead-photo">', 'href="'],
                                 [],
                                 '<div id="region_1"', '<div id="region_2"',
                                 '<div class="widget lead-story layout-3col-feature" data-count="2">', '<div id="region_2"',
                                 None, None))



    sourceList.append(NewsSource('New York Times',
                                 'http://nytimes.com',
                                 ['<a href="'],
                                 ['<article class="story theme-summary"', '<a href="'],
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



    
    #scrape all urls and build data structure
    newsSourceArr=buildNewsSourceArr(sourceList)

    #build the output file HTML
    outputHTML=buildOutput(newsSourceArr)
    #print the output file HTML
    printOutputHTML(outputHTML, '/var/www/html/index.html')


if __name__=="__main__":
    main()
