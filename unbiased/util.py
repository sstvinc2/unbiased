import io
import logging
import os
import pkgutil
import random
import shutil
import time

from PIL import Image
import requests

logger = logging.getLogger('unbiased')


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
    # read in the template html file
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
        timestamp=timestamp,
        utime=utime,
        top_stories=top_stories,
        middle_stories=middle_stories,
        bottom_stories=bottom_stories,
        sources=sourcesStr,
    )

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
    res = requests.get(url, timeout=3)
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
        img = img.resize((target_width * 2, target_height * 2), Image.LANCZOS)
    # TODO: fill with a neutral color instead of just discarding alpha channel
    img = img.convert('RGB')
    # TODO: create retina images
    jpg_name = 'img{}.jpg'.format(index)
    jpg_file = io.BytesIO()
    img.save(jpg_file, 'JPEG')
    jpg_file.seek(0)
    return jpg_name, jpg_file
