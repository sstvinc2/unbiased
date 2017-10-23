from unbiased.sources.base import NewsSource

class NBC(NewsSource):

    name = 'NBC News'
    shortname = 'nbc'
    url = 'https://www.nbcnews.com/'

    bad_urls = ['/opinion/']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        h1s = soup.find('div', class_='js-top-stories-content')\
                .find('div', class_='panel_hero')\
                .a
        h1s = (h1s['href'],)

        rows = soup.find('div', class_='js-top-stories-content')\
                .div.find_all('div', class_='row')
        h2s = []
        for row in rows:
            for fragment in row.find_all('div', class_='media-body'):
                h2s.append(fragment.a['href'])
        h2s = tuple(h2s)

        links = soup.find('div', class_='js-more-topstories')\
                .div.find_all('div', class_='story-link')
        h3s = tuple(x.a['href'] for x in links)

        return h1s, h2s, h3s
