#!/usr/bin/env python3

import argparse
import logging
import time

from unbiased.unbiasedObjects import *
from unbiased.unbiasedFunctions import *
from unbiased.parser import *

logger = logging.getLogger('unbiased')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webroot', default='/var/www/ubiased', help='location to write the output html')
    parser.add_argument('-s', '--scratch', default='/opt/unbiased/scratch', help='writable scratch workspace')
    args = parser.parse_args()

    while True:
        logger.info('Starting crawl')
        run(args.webroot, args.scratch)
        logger.info('Crawl complete. Sleeping for 600s')
        time.sleep(600)

def run(webroot, scratch):
    sourceList=[]

    '''

    SOURCES TO ADD NEXT:
    -ABC
    -REUTERS
    -Town Hall

    '''

    logger.debug('Running with webroot="{}"'.format(webroot))
    logger.debug('Running with scratch="{}"'.format(scratch))


    ### These values have to be the second half of the function name
    ### E.g. Guardian calls buildGuardian(), etc.
    sourceFnArr=['Guardian', 'TheHill', 'NPR', 'BBC', 'NBC', 'CBS',
                 'FoxNews', 'WashTimes', 'CSM', 'ABC'] #'Blaze'

    for source in sourceFnArr:
        logger.info('Crawling {}'.format(source))
        tries=0
        while tries<3:
            time.sleep(tries)
            try:
                fn='build'+source
                possibles = globals().copy()
                possibles.update(locals())
                method = possibles.get(fn)
                src=method(scratch)
                sourceList.append(src)
                break
            except Exception as ex:
                tries+=1
                if tries == 3:
                    logger.error('Build failed. source={} ex={}'.format(source, ex))
                else:
                    logger.debug('Build failed, retrying. source={} ex={}'.format(source, ex))

    #scrape all urls and build data structure
    newsSourceArr=buildNewsSourceArr(sourceList, scratch)

    #build the output file HTML
    outputHTML=buildOutput(newsSourceArr, webroot)

    #print the output file HTML
    printOutputHTML(outputHTML, webroot)


if __name__=="__main__":
    main()
