from unbiased.sources.base import NewsSource

class Fox(NewsSource):

    name = 'Fox News'
    shortname = 'Fox'
    url = 'http://www.foxnews.com'

    bad_titles = ['O&#039;Reilly', 'Fox News', 'Brett Baier', 'Tucker']
    bad_descriptions = ['Sean Hannity']
    bad_authors = ['Bill O\'Reilly', 'Sean Hannity', 'Howard Kurtz']
    bad_imgs = ['http://www.foxnews.com/content/dam/fox-news/logo/og-fn-foxnews.jpg']
    bad_urls = ['http://www.foxnews.com/opinion', 'videos.foxnews.com']

    @classmethod
    def _fetch_urls(cls):
        """
        Returns three tuples of urls, one for each of
        the three tiers.
        """
        soup = cls._fetch_content(cls.url)

        # get primary headline
        h1 = soup.find('div', id='big-top')\
                 .find('div', class_='primary')\
                 .find('h1')\
                 .find('a')['href']
        h1s = (h1,)

        # get secondary headlines
        h2s = soup.find('div', id='big-top').find('div', class_='top-stories').select('li > a')
        h2s = tuple(x['href'] for x in h2s)

        # get tertiary headlines
        h3s = []
        for ul in soup.find('section', id='latest').find_all('ul', recursive=False):
            for li in ul.find_all('li', recursive=False):
                h3s.append(li.find('a')['href'])
        h3s = tuple(h3s)

        return h1s, h2s, h3s
