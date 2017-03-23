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


    ### These values have to be the second half of the function name
    ### E.g. Guardian calls buildGuardian(), etc.
    sourceFnArr=['Guardian', 'TheHill', 'NPR', 'Blaze', 'BBC', 'NBC', 'CBS',
                 'FoxNews', ]
    
    for source in sourceFnArr:
        tries=0
        while tries<3:
            try:
                fn='build'+source
                possibles = globals().copy()
                possibles.update(locals())
                method = possibles.get(fn)
                src=method()
                sourceList.append(src)
                break
            except:
                print('Build error. Looping again: '+source)
                tries+=1
                time.sleep(tries)
    
    #scrape all urls and build data structure
    newsSourceArr=buildNewsSourceArr(sourceList)

    #build the output file HTML
    outputHTML=buildOutput(newsSourceArr)

    #print the output file HTML
    printOutputHTML(outputHTML, '/var/www/html/index.html')


if __name__=="__main__":
    main()
