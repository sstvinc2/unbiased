#!/usr/bin/env python3

import argparse
import time

from unbiased.unbiasedObjects import *
from unbiased.unbiasedFunctions import *
from unbiased.parser import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webroot', default='/var/www/ubiased', help='location to write the output html')
    parser.add_argument('-s', '--scratch', default='/opt/unbiased/scratch', help='writable scratch workspace')
    args = parser.parse_args()

    while True:
        print('-----------------------')
        run(args.webroot, args.scratch)
        print('-----------------------')
        time.sleep(600)

def run(webroot, scratch):
    sourceList=[]

    '''

    SOURCES TO ADD NEXT:
    -ABC
    -REUTERS
    -Town Hall

    '''

    print('running with webroot="{}"'.format(webroot))
    print('running with scratch="{}"'.format(scratch))


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
                src=method(scratch)
                sourceList.append(src)
                break
            except Exception as ex:
                print(ex)
                print('Build error. Looping again: '+source)
                tries+=1
                time.sleep(tries)
    
    #scrape all urls and build data structure
    newsSourceArr=buildNewsSourceArr(sourceList, scratch)

    #build the output file HTML
    outputHTML=buildOutput(newsSourceArr, webroot)

    #print the output file HTML
    printOutputHTML(outputHTML, webroot)


if __name__=="__main__":
    main()
