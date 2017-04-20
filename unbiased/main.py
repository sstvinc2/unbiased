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
    args = parser.parse_args()

    crawl_frequency = 600
    while True:
        logger.info('Starting crawl')
        start = time.time()
        run(args.webroot)
        finish = time.time()
        runtime = finish - start
        sleeptime = crawl_frequency - runtime
        logger.info('Crawl complete in {}s. Sleeping for {}s'.format(int(runtime), int(sleeptime)))
        if sleeptime > 0:
            time.sleep(sleeptime)

def run(webroot):
    sources = []

    '''
    SOURCES TO ADD NEXT:
    -REUTERS
    -Town Hall
    '''

    logger.debug('Running with webroot="{}"'.format(webroot))

    ### These values have to be the second half of the function name
    ### E.g. Guardian calls buildGuardian(), etc.
    sourceFnArr = [
        'Guardian',
        'TheHill',
        'NPR',
        'BBC',
        'NBC',
        'CBS',
        'FoxNews',
        'WashTimes',
        'CSM',
        'ABC',
    ]

    for source in sourceFnArr:
        logger.info('Crawling {}'.format(source))
        tries = 0
        while tries < 3:
            time.sleep(tries)
            try:
                fn = 'build' + source
                possibles = globals().copy()
                possibles.update(locals())
                method = possibles.get(fn)
                src = method()
                sources.append(src)
                break
            except Exception as ex:
                tries += 1
                if tries == 3:
                    logger.error('Build failed. source={} ex={}'.format(source, ex))
                else:
                    logger.debug('Build failed, retrying. source={} ex={}'.format(source, ex))
    logger.info('Parsed home pages for: {}'.format([x.name for x in sources]))

    top_stories, middle_stories, bottom_stories = pickStories(sources)
    logger.info('Picked top stories from: {}'.format([x.source for x in top_stories]))
    logger.info('Picked middle stories from: {}'.format([x.source for x in middle_stories]))
    logger.info('Picked bottom stories from: {}'.format([x.source for x in bottom_stories]))

    # download images
    img_idx = 0
    for story in top_stories:
        story.img = pullImage(story.img, img_idx, webroot, 350, 200)
        img_idx += 1
    for story in middle_stories:
        story.img = pullImage(story.img, img_idx, webroot, 150, 100)
        img_idx += 1

    #build the output file HTML
    outputHTML = buildOutput(top_stories, middle_stories, bottom_stories)

    #print the output file HTML
    writeOutputHTML(outputHTML, webroot)

if __name__=="__main__":
    main()
