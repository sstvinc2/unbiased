#!/usr/bin/env python3

import argparse
import os

from unbiasedObjects import *
from unbiasedFunctions import *
from parser import *
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webroot', default='/var/www/ubiased', help='location to write the output html')
    args = parser.parse_args()

    while True:
        print('-----------------------')
        run(args.webroot)
        print('-----------------------')
        time.sleep(600)

def run(webroot):
    sourceList=[]

    '''

    SOURCES TO ADD NEXT:
    -ABC
    -REUTERS
    -Town Hall

    '''

    print('running with webroot="{}"'.format(webroot))


    ### These values have to be the second half of the function name
    ### E.g. Guardian calls buildGuardian(), etc.
    sourceFnArr=['Guardian', 'TheHill', 'NPR', 'BBC', 'NBC', 'CBS',
                 'FoxNews', 'WashTimes', 'CSM', 'ABC'] #'Blaze'
    
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
    printOutputHTML(outputHTML, os.path.join(webroot, 'index.html'))


if __name__=="__main__":
    main()
