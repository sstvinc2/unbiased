from unbiased.sources.base import NewsSource

class TheWashingtonTimes(NewsSource):

    name = 'The Washington Times'
    shortname = 'WashTimes'
    url = 'http://www.washingtontimes.com/'

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        h1 = soup.find('article', class_='lead-story')\
                .find(class_='article-headline')\
                .a['href']
        h1s = (h1,)

        top_articles = soup.find('section', class_='top-news')\
                .find_all('article', recursive=False)
        h2s = []
        for a in top_articles:
            if a.attrs.get('class') is None:
                h2s.append(a.a['href'])
        h2s = tuple(h2s)

        h3s = soup.find('section', class_='more-from desktop-only')\
                .ul.find_all('a')
        h3s = [x['href'] for x in h3s]
        h3s = tuple(h3s)

        return h1s, h2s, h3s
