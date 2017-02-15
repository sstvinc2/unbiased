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

    blz=buildBlaze()
    sourceList.append(blz)

    bbc=buildBBC()
    sourceList.append(bbc)

    nbc=buildNBC()
    sourceList.append(nbc)

    cbs=buildCBS()
    sourceList.append(cbs)

    wkl=buildWeeklyStandard()
    sourceList.append(wkl)

    #nyt=buildNYT()
    #sourceList.append(nyt)

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
