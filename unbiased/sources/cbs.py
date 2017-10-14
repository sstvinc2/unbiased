from unbiased.sources.base import NewsSource

class CBS(NewsSource):

    name = 'CBS News'
    shortname = 'cbs'
    url = 'https://www.cbsnews.com/'

    bad_titles = ['60 Minutes']
    bad_descriptions = ['60 Minutes']
    bad_urls = ['whats-in-the-news-coverart']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        # get primary headline
        h1 = soup.find('h1', class_='title')
        # sometimes they lead with a video
        # if so, we'll pull the first h2 into the h1 slot later
        if h1 is not None:
            h1s = (h1.a['href'],)

        # get secondary headlines
        h2s = soup.find('div', attrs={'data-tb-region': 'Big News Area Side Assets'})\
                .ul.find_all('li', attrs={'data-tb-region-item': True})
        h2s = tuple(x.a['href'] for x in h2s)
        if h1 is None:
            h1s = (h2s[0],)
            h2s = tuple(h2s[1:])

        # get tertiary headlines
        h3s = soup.find('div', attrs={'data-tb-region': 'Hard News'})\
                .ul.find_all('li', attrs={'data-tb-region-item': True})
        h3s = tuple(x.a['href'] for x in h3s[:5])

        return h1s, h2s, h3s
