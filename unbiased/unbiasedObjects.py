import logging

logger = logging.getLogger('unbiased')

class Article():
    title=''
    url=''
    img=''
    description=''
    source=''
    author=''

    def __init__(self, title, url, img, description, source, author):
        self.title=title
        self.url=url
        self.img=img
        self.description=description
        self.source=source
        self.author=author

    def __str__(self):
        return '-----------\n'+self.title+'\n'+self.author+'\n'+self.source+'\n'+self.description+'\n'+self.url+'\n'+self.img+'\n'+'-----------'


class NewsSource2():
    name=''
    url=''
    h1Arr=[]
    h2Arr=[]
    h3Arr=[]
    def __init__(self, name, url, h1Arr, h2Arr, h3Arr):
        self.name=name
        self.url=url
        self.h1Arr=h1Arr
        self.h2Arr=h2Arr
        self.h3Arr=h3Arr
        

        
class NewsSource():
    name=''
    url=''
    #multiple start values to step through file. end value default to '"'
    h1SectionDividerStart=None
    h1SectionDividerEnd=None
    h1DelStart=[]
    h1DelEnd='"'
    h2SectionDividerStart=None
    h2SectionDividerEnd=None
    h2DelStart=[]
    h2DelEnd='"'
    h3SectionDividerStart=None
    h3SectionDividerEnd=None
    h3DelStart=[]
    h3DelEnd='"'
    #arrays of Article object types
    h1Arr=None
    h2Arr=None
    h3Arr=None
    #url to attach to stub links
    stubURL=''
    
    def __init__(self, name, url,
                 h1DelStart, h2DelStart, h3DelStart,
                 h1SectionDividerStart=None, h1SectionDividerEnd=None,
                 h2SectionDividerStart=None, h2SectionDividerEnd=None,
                 h3SectionDividerStart=None, h3SectionDividerEnd=None,
                 stubURL=None):
        self.name=name
        self.url=url
        self.h1DelStart=h1DelStart
        self.h2DelStart=h2DelStart
        self.h3DelStart=h3DelStart
        self.h1SectionDividerStart=h1SectionDividerStart
        self.h2SectionDividerStart=h2SectionDividerStart
        self.h3SectionDividerStart=h3SectionDividerStart
        self.h1SectionDividerEnd=h1SectionDividerEnd
        self.h2SectionDividerEnd=h2SectionDividerEnd
        self.h3SectionDividerEnd=h3SectionDividerEnd
        self.h1Arr=[]
        self.h2Arr=[]
        self.h3Arr=[]
        self.stubURL=stubURL

    def addArticle(self, article, level):
        if level==1:
            self.h1Arr.append(article)
        elif level==2:
            self.h2Arr.append(article)
        elif level==3:
            self.h3Arr.append(article)
        else:
            logger.debug("Invalid level in NewsSource.addArtlce: " + level)

