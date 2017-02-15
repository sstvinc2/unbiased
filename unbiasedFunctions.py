from unbiasedObjects import *
import os
import random
import time


#take in a url and delimiters, return twitter card
def buildArticle(url, sourceName):#, titleDelStart, titleDelEnd, imgDelStart, imgDelEnd):

    '''#PRINT DEBUGGING
    print(sourceName)
    print(url)
    print()
    '''
    
    #download url
    os.system('wget -q -O scratch/temp_article.html --no-check-certificate '+url)

    #read the file in
    f=open('scratch/temp_article.html', 'r', encoding="utf8")
    content=f.read()
    f.close()

    try:
        #because the quote separator could be ' or ", trim to just before it then lop it off
        img=content.split('og:image" content=')[1][1:].split('>')[0]
        if img[-1]=='/':
            img=img[:-1].strip()
        img=img[:-1]

        title=content.split('og:title" content=')[1][1:].split('>')[0]
        if title[-1]=='/':
            title=title[:-1].strip()
        title=title[:-1]

        author=''
        authorTags=['article:author', 'dc.creator']
        for tag in authorTags:
            if tag in content:
                author=content.split(tag+'" content=')[1][1:].split('>')[0]
                author=author[:-1]
                break

        description=content.split('og:description" content=')[1][1:].split('>')[0]
        if description[-1]=='/':
            description=description[:-1].strip()
        description=description[:-1]

        a=Article(title, url, img, description, sourceName, author)
        return a

    except:
        print("Article parsing error in buildArticle() for URL: "+url+" in source"+sourceName)
        return None


#take in a read main source file (e.g. from nytimes.com) and return lists of the urls for stories
def extractURLs(content, source):
    h1s=[]
    h2s=[]
    h3s=[]

    try:
        h1=content
        if source.h1SectionDividerStart!=None:
            h1=h1.split(source.h1SectionDividerStart)[1]
        if source.h1SectionDividerEnd!=None:
            h1=h1.split(source.h1SectionDividerEnd)[0]
        for delim in source.h1DelStart:
            h1=h1.split(delim)[1]
        h1=h1.split(source.h1DelEnd)[0]
        if '.com' not in h1:
            if source.stubURL!=None:
                h1=source.stubURL+h1
            else:
                h1=source.url+h1
        h1s.append(h1)
    except:
        print("Parse error in extractURLs: "+source.name+" h1")
        h1s=None
        
    try:
        h2=content
        if source.h2SectionDividerStart!=None:
            h2=h2.split(source.h2SectionDividerStart, 1)[1]
        if source.h2SectionDividerEnd!=None:
            h2=h2.split(source.h2SectionDividerEnd, 1)[0]

        while source.h2DelStart[0] in h2:
            x=h2
            for delim in source.h2DelStart:
                x=x.split(delim)[1]
                h2=h2.split(delim, 1)[1]
            x=x.split(source.h2DelEnd)[0]
            h2=h2.split(source.h2DelEnd, 1)[1]
            if '.com' not in x:
                if source.stubURL!=None:
                    x=source.stubURL+x
                else:
                    x=source.url+x
            h2s.append(x)
    except:
        print("Parse error in extractURLs: "+source.name+" h2")
        h2s=None

    return h1s, h2s, h3s


def buildOutput(newsSourceArr):
    #read in the template html file
    f=open('html_template/template.html', 'r')
    template=f.read()
    f.close()
    
    #set the random order for sources
    h1RandomSources=random.sample(range(len(newsSourceArr)), 4)
    h2RandomSources=random.sample(range(len(newsSourceArr)), 6)

    #replace html template locations with data from newsSourceArr
    for i in range(len(h1RandomSources)):
        source=newsSourceArr[h1RandomSources[i]]
        randomArticle=random.sample(range(len(source.h1Arr)), 1)[0]
        article=source.h1Arr[randomArticle]
        template=template.replace('xxURL1-'+str(i+1)+'xx', article.url)
        '''
        r=open('/var/www/html/redirects/h1-'+str(i+1)+'.html', 'w')
        r.write('<html><head><script type="text/javascript">window.location="'+article.url+'"</script></head></html>')
        r.close()
        '''
        template=template.replace('xxTitle1-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg1-'+str(i+1)+'xx', article.img)
        desc=article.description
        if len(desc)>144:
            desc=desc[:141]
            desc=desc.split()[:-1]
            desc=' '.join(desc)+' ...'
        template=template.replace('xxDesc1-'+str(i+1)+'xx', desc)


    for i in range(len(h2RandomSources)):
        source=newsSourceArr[h2RandomSources[i]]
        randomArticle=random.sample(range(len(source.h2Arr)), 1)[0]
        article=source.h2Arr[randomArticle]
        template=template.replace('xxURL2-'+str(i+1)+'xx', article.url)
        '''
        r=open('/var/www/html/redirects/h2-'+str(i+1)+'.html', 'w')
        r.write('<html><head><script type="text/javascript">window.location="'+article.url+'"</script></head></html>')
        r.close()
        '''
        template=template.replace('xxTitle2-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg2-'+str(i+1)+'xx', article.img)

    sourcesStr=''
    for i in range(len(newsSourceArr)-1):
        sourcesStr+=newsSourceArr[i].name+', '
    sourcesStr+=newsSourceArr[-1].name
    print('Successfully parsed: '+sourcesStr)
    template=template.replace('xxSourcesxx', sourcesStr)
        

    #return updated text
    return template

def printOutputHTML(outputHTML, outFile):
    timestamp=time.strftime("%a, %b %-d, %-I:%M%P %Z", time.localtime())
    outputHTML=outputHTML.replace('xxTimexx', timestamp)
    
    f=open(outFile, 'w')
    f.write(outputHTML)
    f.close()

def buildNewsSourceArr(sourceList):

    #build the data structure
    i=0
    listLen=len(sourceList)
    while i < listLen:
        source=sourceList[i]

        if type(source) is NewsSource2:
            i+=1
            continue

        url=source.url

        #download file
        os.system('wget -q -O scratch/temp'+str(i)+'.html --no-check-certificate '+url)

        #read file
        f=open('scratch/temp'+str(i)+'.html', 'r', encoding="utf8")
        content=f.read()
        f.close()
        
        #delete file MAYBE DON'T DO THIS? CAUSES OS ERRORS
        #os.remove('scratch/temp'+str(i)+'.html')

        #add stories etc to the NewsSource object
        h1s, h2s, h3s=extractURLs(content, source)
        
        #build the Article objects and add to newsSource's appropriate list
        if h1s!=None and h2s!=None:
            for url in h1s:
                article=buildArticle(url, source.name)
                if article!=None: source.addArticle(article, 1) #sourceList[i].h1Arr.append(article)
            for url in h2s:
                article=buildArticle(url, source.name)
                if article!=None: sourceList[i].h2Arr.append(article)
            for url in h3s:
                article=buildArticle(url, source.name)
                if article!=None: sourceList[i].h3Arr.append(article)
            i+=1
        else:
            sourceList.remove(source)
            listLen-=1

            
    #return the original sourceList,
    #since everything should have been modified in place
    return sourceList        
