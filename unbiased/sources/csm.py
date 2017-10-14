from unbiased.sources.base import NewsSource

class CSM(NewsSource):

    name = 'Christian Science Monitor'
    shortname = 'csm'
    url = 'https://www.csmonitor.com/USA'

    bad_titles = ['Change Agent']
    bad_imgs = ['csm_logo']
    bad_urls = ['difference-maker']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        # get primary headline
        h1 = soup.find('div', id='block-0-0')\
                .find('h3', class_='story_headline')\
                .a['href']
        h1s = (h1,)

        # get secondary headlines
        h2_blocks = soup.find_all('div', id=['block-1-0', 'block-0-1'])
        h2s = []
        for block in h2_blocks:
            hblocks = block.find_all('h3', class_='story_headline')
            for hblock in hblocks:
                h2s += [x for x in hblock.find_all('a') if 'first-look' not in x['href']]
        h2s = tuple(x['href'] for x in h2s)

        # get tertiary headlines
        h3_blocks = soup.find_all('div', id='block-0-2')
        h3s = []
        for block in h3_blocks:
            hblocks = block.find_all('h3', class_='story_headline')
            for hblock in hblocks:
                h3s += [x for x in hblock.find_all('a') if 'first-look' not in x['href']]
        h3s = tuple(x['href'] for x in h3s)

        return h1s, h2s, h3s
