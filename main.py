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

    '''

    SOURCES TO ADD NEXT:
    -ABC
    -REUTERS

    '''

    #for some reason, The Guardian sometimes just doesn't work right?
    #loop until it gets it right
    '''
    h1='https://www.theguardian.com/us'
    looped=False
    while h1=='https://www.theguardian.com/us':
        try:
            gdn=buildGuardian()
            h1=gdn.h1Arr[0]
        except:
            print('The Guardian: build error. Looping again.')
        looped=True
    '''
    gdn=buildGuardian()
    sourceList.append(gdn)

    hil=buildTheHill()
    sourceList.append(hil)

    #nyt=buildNYT()
    #sourceList.append(nyt)

    npr=buildNPR()
    sourceList.append(npr)

    blz=buildBlaze()
    sourceList.append(blz)

    bbc=buildBBC()
    sourceList.append(bbc)

    nbc=buildNBC()
    sourceList.append(nbc)

    cbs=buildCBS()
    sourceList.append(cbs)

    #Weekly standard just doesn't update frequently enough
    #wkl=buildWeeklyStandard()
    #sourceList.append(wkl)

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
