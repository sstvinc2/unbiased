from unbiased.sources.base import NewsSource

class NPR(NewsSource):

    name = 'NPR News'
    shortname = 'npr'
    url = 'http://www.npr.org/sections/news/'

    bad_titles = ['The Two-Way']
    bad_authors = ['Domenico Montanaro']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        featured = soup.find('div', class_='featured-3-up')\
                .find_all('article', recursive=False)

        h1s = featured[:1]
        h1s = tuple(x.find('h2', class_='title').a['href'] for x in h1s)
        h2s = featured[1:]
        h2s = tuple(x.find('h2', class_='title').a['href'] for x in h2s)

        # get tertiary headlines
        h3s = soup.find('div', id='overflow')\
                .find_all('article', recursive=False)
        h3s = tuple(x.find('h2', class_='title').a['href'] for x in h3s[:5])

        return h1s, h2s, h3s
