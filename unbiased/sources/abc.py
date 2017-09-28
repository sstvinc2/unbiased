from unbiased.sources.base import NewsSource

class ABC(NewsSource):

    name = 'ABC News'
    shortname = 'ABC'
    url = 'http://abcnews.go.com/'

    @classmethod
    def _fetch_urls(cls):
        """
        Returns three tuples of urls, one for each of
        the three tiers.
        """
        soup = cls._fetch_content(cls.url)

        # get primary headline
        h1 = soup.find('article', class_='hero')\
            .find('div', class_='caption-wrapper').h1.a['href']
        h1s = (h1,)
        print(h1)

        # get secondary headlines
        h2s = soup.find('div', id='row-2')\
            .find_all('article', class_='card single row-item')
        h2s = tuple(x.find('div', class_='caption-wrapper').h1.a['href'] for x in h2s)

        # get tertiary headlines
        h3s = soup.find('div', id='row-1')\
            .find('article', class_='headlines')\
            .find('div', id='tab-content')\
            .find_all('li', class_=['story', 'wirestory'])
        h3s = tuple(x.div.h1.a['href'] for x in h3s)

        return h1s, h2s, h3s

    @classmethod
    def _normalize_url(cls, url):
        """
        ABC News urls include an 'id' query param that we need to
        keep in order for the URL to work.
        """
        return NewsSource._normalize_url(url, ['id'])
