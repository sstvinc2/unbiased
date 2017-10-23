#!/usr/bin/env python3

import argparse
import io
import logging
import logging.config
import os
import time

from unbiased.util import pickStories, pullImage, buildOutput, write_files, write_static_files
from unbiased.sources import get_sources

logger = logging.getLogger('unbiased')

logging_config = {
    'version': 1,
    'formatters': {
        'console': {
            'format': '%(levelname)s %(filename)s:%(lineno)d %(message)s',
        },
        'file': {
            'format': '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'console',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'file',
            'filename': '',
            'maxBytes': 1024 * 1024,
            'backupCount': 3,
        },
        'web': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'file',
        },
    },
    'loggers': {
        'unbiased': {
            'handlers': ['console', 'file', 'web'],
        },
    },
    'root': {
        'level': 'DEBUG',
    }
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('webroot', help='location to write html output')
    parser.add_argument('-l', '--log-dir', help='location to write detailed logs')
    parser.add_argument('-d', '--debug', action='store_true', help='run in debug mode')
    parser.add_argument('-o', '--oneshot', action='store_true', help='run once and exit')
    parser.add_argument('-s', '--sources', type=lambda x: x.split(','), default=None)
    args = parser.parse_args()

    if args.log_dir:
        logging_config['handlers']['file']['filename'] = os.path.join(args.log_dir, 'unbiased.debug.log')
    else:
        logging_config['loggers']['unbiased']['handlers'].remove('file')
        del logging_config['handlers']['file']
    if args.debug:
        logging_config['handlers']['console']['level'] = 'DEBUG'
    web_log_stream = io.StringIO()
    logging_config['handlers']['web']['stream'] = web_log_stream
    logging.config.dictConfig(logging_config)

    crawl_frequency = 600
    while True:
        web_log_stream.seek(0)
        web_log_stream.truncate()
        logger.info('Starting crawl')
        start = time.time()
        run(args.webroot, args.sources, web_log_stream, args.debug)
        finish = time.time()
        runtime = finish - start
        sleeptime = crawl_frequency - runtime
        logger.info('Crawl complete in {}s. Sleeping for {}s'.format(int(runtime), int(sleeptime)))
        if args.oneshot:
            break
        if sleeptime > 0:
            time.sleep(sleeptime)


def run(webroot, source_names, web_log_stream, debug_mode=False):

    logger.debug('Running with webroot="{}" for sources="{}"'.format(webroot, source_names))

    sources = get_sources()
    if source_names is None:
        sources = sources.values()
    else:
        sources = [sources[x] for x in source_names]

    built_sources = []
    for source in sources:
        logger.info('Crawling {}'.format(source.name))
        tries = 0
        while tries < 3:
            time.sleep(tries)
            try:
                built_sources.append(source.build())
                break
            except Exception as ex:
                if debug_mode is True:
                    raise
                tries += 1
                if tries == 3:
                    logger.error('Build failed. source={} ex={}'.format(source.name, ex))
                else:
                    logger.debug('Build failed, retrying. source={} ex={}'.format(source.name, ex))
    sources = tuple(built_sources)
    logger.info('Parsed home pages for: {}'.format([x.name for x in sources]))

    top_stories, middle_stories, bottom_stories = pickStories(sources)
    logger.info('Picked top stories from: {}'.format([x.source for x in top_stories]))
    logger.info('Picked middle stories from: {}'.format([x.source for x in middle_stories]))
    logger.info('Picked bottom stories from: {}'.format([x.source for x in bottom_stories]))

    files_to_write = {}

    # download images
    img_idx = 0
    for story in top_stories:
        story.img, img_jpg = pullImage(story.img, img_idx, webroot, 350, 200)
        files_to_write[story.img] = img_jpg
        img_idx += 1
    for story in middle_stories:
        story.img, img_jpg = pullImage(story.img, img_idx, webroot, 150, 100)
        files_to_write[story.img] = img_jpg
        img_idx += 1
    logger.info('Downloaded images')

    # build the output file HTML
    output_html = buildOutput(top_stories, middle_stories, bottom_stories)
    output_html = io.BytesIO(output_html.encode('utf8'))
    files_to_write['index.html'] = output_html
    files_to_write['log.txt'] = io.BytesIO(web_log_stream.getvalue().encode('utf8'))

    write_files(files_to_write, webroot)
    write_static_files(webroot)


if __name__ == "__main__":
    main()
