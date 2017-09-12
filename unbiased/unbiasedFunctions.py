import html
import io
import logging
import os
import pkgutil
import random
import re
import shutil
import time
import urllib.parse

from PIL import Image
import requests

logger = logging.getLogger('unbiased')

#take in a url and delimiters, return twitter card
def buildArticle(url, sourceName, encoding=None):#, titleDelStart, titleDelEnd, imgDelStart, imgDelEnd):

    debugging=False
    if debugging:
        logger.debug(sourceName)
        logger.debug(url)

    url_parts = urllib.parse.urlparse(url)
    scheme = url_parts.scheme

    #download url
    try:
        res = requests.get(url)
    except Exception as ex:
        logger.debug("""ARTICLE DOWNLOADING ERROR
        SOURCE:\t{}
        URL:\t{}""".format(sourceName, url))
        return None

    if res.status_code == 200:
        content = res.text
    else:
        logger.debug("""ARTICLE DOWNLOADING ERROR
        SOURCE:\t{}
        URL:\t{}""".format(sourceName, url))
        return None

    try:
        if sourceName=='The Guardian US':
            #The Guardian puts an identifying banner on their og:images
            #grab the main image from the page instead

            #scenario 1: regular image
            if '<img class="maxed' in content:
                img=content.split('<img class="maxed', 1)[1]
                img=img.split('src="', 1)[1].split('"')[0]
            #scenario 2: video in image spot
            elif '<meta itemprop="image"' in content:
                img=content.split('<meta itemprop="image"', 1)[1]
                img=img.split('content="', 1)[1].split('"')[0]
            #scenario 3: photo essays
            elif '<img class="immersive-main-media__media"' in content:
                img=content.split('<img class="immersive-main-media__media"', 1)[1]
                img=img.split('src="', 1)[1].split('"')[0]
            img = html.unescape(img)

        else:
            if 'og:image' in content:
                img=content.split('og:image" content=')[1][1:].split('>')[0]
            elif sourceName=='ABC News':
                img='https://c1.staticflickr.com/7/6042/6276688407_12900948a2_b.jpgX'
            if img[-1]=='/':
                #because the quote separator could be ' or ",
                #trim to just before it then lop it off
                img=img[:-1].strip()
            img=img[:-1]
        # fix the scheme if it's missing
        img = urllib.parse.urlparse(img, scheme=scheme).geturl()

        if debugging:
            logger.debug(img)

        title=content.split('og:title" content=')[1][1:].split('>')[0]
        if title[-1]=='/':
            title=title[:-1].strip()
        title=title[:-1]

        if debugging:
            logger.debug(title)


        author=''
        if sourceName=='The Blaze':
            if 'class="article-author">' in content:
                author=content.split('class="article-author">')[1].split('<')[0]
            elif 'class="article-author" href="' in content:
                author=content.split('class="article-author" href="')[1]
                author=author.split('>')[1].split('<')[0].strip()
        else:
            authorTags=['article:author', 'dc.creator', 'property="author']
            for tag in authorTags:
                if tag in content:
                    author=content.split(tag+'" content=')[1][1:].split('>')[0]
                    author=author[:-1]
                    #trim an extra quotation mark for The Hill
                    if sourceName=='The Hill':
                        author=author.split('"', 1)[0]
                    break

        if debugging:
            logger.debug(author)


        if 'og:description' in content:
            description=content.split('og:description" content=')[1][1:].split('>')[0]
            if description[-1]=='/':
                description=description[:-1].strip()
            description=description[:-1]
        else:
            if sourceName=='The Hill':
                description=content.split('div class="field-items"')[-1]
                description=re.sub('<[^<]+?>', '', description)
                description=description[1:200]
            else:
                logger.debug("SHOULDN'T GET HERE")

        #strip out self-references
        description=description.replace(sourceName+"'s", '***')
        description=description.replace(sourceName+"'", '***')
        description=description.replace(sourceName, '***')

        if debugging:
            logger.debug(description)


        a=Article(html.unescape(title), url, img, html.unescape(description), sourceName, html.unescape(author))
        return a

    except Exception:
        logger.debug("""ARTICLE PARSING ERROR
        SOURCE:\t{}
        URL:\t{}""".format(sourceName, url))
        return None


def pick_randoms(story_lists, length, per_source):
    """
    Return a randomly chosen list of 'length' stories, picking at
    most 'per_source' stories from each source.
    """
    # TODO: weighting is incorrect if a source has fewer than 'per_source' articles
    urandom = random.SystemRandom()
    candidates = []
    for stories in story_lists:
        indexes = list(range(len(stories)))
        urandom.shuffle(indexes)
        random_indexes = indexes[:per_source]
        candidates.extend([stories[x] for x in random_indexes])
    indexes = list(range(len(candidates)))
    urandom.shuffle(indexes)
    random_indexes = indexes[:length]
    return tuple(candidates[x] for x in random_indexes)


def pickStories(newsSourceArr):
    h1s = pick_randoms([x.h1s for x in newsSourceArr], 4, 1)
    h2s = pick_randoms([x.h2s for x in newsSourceArr], 6, 2)
    h3s = pick_randoms([x.h3s for x in newsSourceArr], 12, 2)
    return h1s, h2s, h3s

def buildOutput(top_stories, middle_stories, bottom_stories):
    #read in the template html file
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader('unbiased', 'html_template'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('unbiased.jinja.html')

    timestamp = time.strftime("%a, %b %-d, %-I:%M%P %Z", time.localtime())
    utime = int(time.time())

    sourcesStr = ', '.join(set([x.source for x in top_stories] + [x.source for x in middle_stories] + [x.source for x in bottom_stories]))

    html = template.render(
        timestamp = timestamp,
        utime = utime,
        top_stories = top_stories,
        middle_stories = middle_stories,
        bottom_stories = bottom_stories,
        sources = sourcesStr,
    )

    #return updated text
    return html

def write_files(files_to_write, outDir):
    for name, bytesio in files_to_write.items():
        with open(os.path.join(outDir, name), 'wb') as fp:
            shutil.copyfileobj(bytesio, fp)

def write_static_files(outDir):
    # copy over static package files
    for filename in ['unbiased.css', 'favicon.ico', 'favicon.png', 'apple-touch-icon.png']:
        data = pkgutil.get_data('unbiased', os.path.join('html_template', filename))
        with open(os.path.join(outDir, filename), 'wb') as fp:
            fp.write(data)

def pullImage(url, index, webroot, target_width=350, target_height=200):
    extension = url.split('.')[-1].split('?')[0]
    img_name = 'img{}.{}'.format(index, extension)
    res = requests.get(url)
    if res.status_code == 200:
        content = res.content
    else:
        logger.debug('Image not found: url={}'.format(url))
        return ''
    img = Image.open(io.BytesIO(content))
    # crop to aspect ratio
    target_ar = target_width / target_height
    left, top, right, bottom = img.getbbox()
    height = bottom - top
    width = right - left
    ar = width / height
    if target_ar > ar:
        new_height = (target_height / target_width) * width
        bbox = (left, top + ((height - new_height) / 2), right, bottom - ((height - new_height) / 2))
        img = img.crop(bbox)
    elif target_ar < ar:
        new_width = (target_width / target_height) * height
        bbox = (left + ((width - new_width) / 2), top, right - ((width - new_width) / 2), bottom)
        img = img.crop(bbox)
    # resize if larger
    if target_width * 2 < width or target_height * 2 < height:
        img = img.resize((target_width*2, target_height*2), Image.LANCZOS)
    # TODO: fill with a neutral color instead of just discarding alpha channel
    img = img.convert('RGB')
    # TODO: create retina images
    jpg_name = 'img{}.jpg'.format(index)
    jpg_file = io.BytesIO()
    out_file = os.path.join(webroot, jpg_name)
    img.save(jpg_file, 'JPEG')
    jpg_file.seek(0)
    return jpg_name, jpg_file
