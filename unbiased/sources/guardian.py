import html

from unbiased.sources.base import NewsSource

class TheGuardian(NewsSource):

    name = 'The Guardian'
    shortname = 'Guardian'
    url = 'https://www.theguardian.com/us'

    bad_authors = ['Tom McCarthy', 'Andy Hunter']
    bad_urls = ['https://www.theguardian.com/profile/ben-jacobs']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        url_groups = []
        for htag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            hblocks = soup.find('section', id='headlines').find_all(htag)
            urls = [x.a['href'] for x in hblocks]
            url_groups.append(urls)
        url_groups = [x for x in url_groups if len(url_groups) > 0]
        if len(url_groups) < 3:
            raise Exception('not enough article groups on Guardian home page!')

        return tuple(url_groups[0]), tuple(url_groups[1]), tuple(url_groups[2])

    @classmethod
    def _get_image(cls, soup):
        if soup.find('img', class_='maxed'):
            img =  soup.find('img', class_='maxed')['src']
        if soup.find('meta', itemprop='image'):
            img = soup.find('meta', itemprop='image')['content']
        if soup.find('img', class_='immersive-main-media__media'):
            img = soup.find('img', class_='immersive-main-media__media')['src']
        return html.unescape(img)
