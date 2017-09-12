import collections
import html
import logging
import urllib

from bs4 import BeautifulSoup
import requests

logger = logging.getLogger('unbiased')

class Article(object):

    def __init__(self, source, title, author, description, url, img):
        self.source = source
        self.title = title
        self.author = author
        self.description = description
        self.url = url
        self.img = img

    def __repr__(self):
        return 'Article({}, {}, {}, {}, {}, {})'.format(self.source, self.title, self.author, self.description, self.url, self.img)

class NewsSource(object):
    """
    Abstract base class.
    To implement:
     - set 'name', 'shortname', and 'url'
     - set 'bad_' variables to blacklist terms and phrases
     - implement '_fetch_urls()', which should return three tuples
       of urls, one for each tier
     - override any of the '_get_*()' functions as necessary
    """
    # TODO: replace all string parsing with bs4

    name = None
    shortname = None
    url = None

    bad_titles = None
    bad_authors = None
    bad_descriptions = None
    bad_imgs = None
    bad_urls = None

    def __init__(self, h1s, h2s, h3s):
        self.h1s = h1s
        self.h2s = h2s
        self.h3s = h3s

    @classmethod
    def build(cls):
        h1s, h2s, h3s = cls._fetch_urls()
        h1s = tuple(cls._normalize_url(x) for x in h1s)
        h2s = tuple(cls._normalize_url(x) for x in h2s)
        h3s = tuple(cls._normalize_url(x) for x in h3s)
        h1s, h2s, h3s = cls._remove_duplicates(h1s, h2s, h3s)
        h1s, h2s, h3s = cls._fetch_articles(h1s, h2s, h3s)
        h1s, h2s, h3s = cls._remove_all_bad_stories(h1s, h2s, h3s)
        return cls(h1s, h2s, h3s)

    @classmethod
    def _fetch_content(cls, url):
        res = requests.get(url)
        if res.status_code == 200:
            content = res.text
        else:
            raise Exception("Failed to download {}".format(url))
        return BeautifulSoup(content, 'lxml')

    @classmethod
    def _normalize_url(cls, url, scheme='http'):
        """
        Make sure they have a scheme.
        Trim any query string, params, or fragments.
        """
        url = urllib.parse.urlparse(url)
        url = (url.scheme or scheme, url.netloc, url.path, '', '', '')
        return urllib.parse.urlunparse(url)

    @classmethod
    def _remove_duplicates(cls, h1s, h2s, h3s):
        h2s = tuple(x for x in h2s if x not in h1s)
        h3s = tuple(x for x in h3s if x not in h1s and x not in h2s)
        return h1s, h2s, h3s

    @classmethod
    def _remove_bad_stories(cls, articles, element, filters):
        if filters is None:
            return articles
        new_articles = []
        for article in articles:
            save = True
            for f in filters:
                if f in getattr(article, element):
                    save = False
                    break
            if save:
                new_articles.append(article)
        return tuple(new_articles)

    @classmethod
    def _remove_all_bad_stories(cls, h1s, h2s, h3s):
        new_articles = []
        for articles in [h1s, h2s, h3s]:
            articles = cls._remove_bad_stories(articles, 'title', cls.bad_titles)
            articles = cls._remove_bad_stories(articles, 'description', cls.bad_descriptions)
            articles = cls._remove_bad_stories(articles, 'author', cls.bad_authors)
            articles = cls._remove_bad_stories(articles, 'img', cls.bad_imgs)
            articles = cls._remove_bad_stories(articles, 'url', cls.bad_urls)
            new_articles.append(articles)
        if len(new_articles[0]) == 0 and len(new_articles[1]) > 0:
            new_articles[0].append(new_articles[1].pop())
        return tuple(tuple(x) for x in new_articles)

    @classmethod
    def _fetch_articles(cls, h1s, h2s, h3s):
        ret = []
        for urls in [h1s, h2s, h3s]:
            articles = []
            for url in urls:
                article = cls._fetch_article(url)
                if article is not None:
                    articles.append(article)
            ret.append(articles)
        return tuple(tuple(x) for x in ret)

    @classmethod
    def _fetch_article(cls, url):
        #soup = cls._fetch_content(url)

        logger.debug(cls.name)
        logger.debug(url)

        url_parts = urllib.parse.urlparse(url)
        scheme = url_parts.scheme

        # download url
        try:
            res = requests.get(url)
        except Exception as ex:
            logger.debug("""ARTICLE DOWNLOADING ERROR
            SOURCE:\t{}
            URL:\t{}""".format(cls.name, url))
            return None

        if res.status_code == 200:
            content = res.text
        else:
            logger.debug("""ARTICLE DOWNLOADING ERROR
            SOURCE:\t{}
            URL:\t{}""".format(cls.name, url))
            return None

        try:
            img = cls._get_image(content)
            img = urllib.parse.urlparse(img, scheme=scheme).geturl()
            logger.debug(img)

            title = cls._get_title(content)
            logger.debug(title)

            author = cls._get_author(content)
            logger.debug(author)

            description = cls._get_description(content)
            logger.debug(description)
            description = cls._remove_self_refs(description)
            logger.debug(description)
        except Exception:
            logger.debug("""ARTICLE PARSING ERROR
            SOURCE:\t{}
            URL:\t{}""".format(cls.name, url))
            return None

        return Article(cls.name, title, author, description, url, img)

    @classmethod
    def _get_image(cls, content):
        img = content.split('og:image" content=')[1][1:].split('>')[0]
        if img[-1] == '/':
            #because the quote separator could be ' or ",
            #trim to just before it then lop it off
            img = img[:-1].strip()
        img = img[:-1]
        return img

    @classmethod
    def _get_title(cls, content):
        title=content.split('og:title" content=')[1][1:].split('>')[0]
        if title[-1]=='/':
            title=title[:-1].strip()
        title=title[:-1]
        return title

    @classmethod
    def _get_author(cls, content):
        author = ''
        authorTags = ['article:author', 'dc.creator', 'property="author']
        for tag in authorTags:
            if tag in content:
                author = content.split(tag+'" content=')[1][1:].split('>')[0]
                author = author[:-1]
                break
        return author

    @classmethod
    def _get_description(cls, content):
        description = content.split('og:description" content=')[1][1:].split('>')[0]
        if description[-1] == '/':
            description = description[:-1].strip()
        description = description[:-1]
        return description

    @classmethod
    def _remove_self_refs(cls, description):
        description = description.replace(cls.name+"'s", '***')
        description = description.replace(cls.name+"'", '***')
        description = description.replace(cls.name, '***')
        return description
