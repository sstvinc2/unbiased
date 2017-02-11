from unbiasedObjects import *
import os
import random
import time

#take in a url and delimiters, return twitter card
def buildArticle(url, sourceName):#, titleDelStart, titleDelEnd, imgDelStart, imgDelEnd):

    print(sourceName)
    print(url)
    print()
    #download url
    os.system('wget -q -O scratch/temp_article.html --no-check-certificate '+url)

    #read the file in
    f=open('scratch/temp_article.html', 'r', encoding="utf8")
    content=f.read()
    f.close()

    #because the quote separator could be ' or ", trim to just before it then lop it off
    img=content.split('og:image" content=')[1][1:].split('>')[0]
    if img[-1]=='/':
        img=img[:-1].strip()
    img=img[:-1]
    
    title=content.split('og:title" content=')[1][1:].split('>')[0]
    if title[-1]=='/':
        title=title[:-1].strip()
    title=title[:-1]

    description=content.split('og:description" content=')[1][1:].split('>')[0]
    if description[-1]=='/':
        description=description[:-1].strip()
    description=description[:-1]
    
    a=Article(title, url, img, description, sourceName)
    return a


#do the hardcore HTML parsing
def splitHTML(content, sectionDividerStart, sectionDividerEnd, delStart, delEnd):
    retArr=[]
    
    if sectionDividerStart!=None:
        content=content.split(sectionDividerStart)[1]
    if sectionDividerEnd!=None:
        content=content.split(sectionDividerEnd)[0]
    if delStart!=[]:
        while True:
            x=content
            for delim in delStart:
                if delim in content:
                    x=content.split(delim)[1]
            x=x.split(delEnd)[0]
            if x not in retArr:
                retArr.append(x)   
            content=content.split(delStart[0], 1)
            if(len(content)==1):
                break
            else:
                content=content[1:][0]

    return retArr
    


'''
**********************8

Need to fix this function to use splitHTML() and actually loop through
all of the links instead of just using the first one.

************************
'''

#take in a read main source file (e.g. from nytimes.com) and return lists of the urls for stories
def extractURLs(content, source):
    h1s=[]
    h2s=[]
    h3s=[]

    h1=content
    if source.h1SectionDividerStart!=None:
        h1=h1.split(source.h1SectionDividerStart)[1]
    if source.h1SectionDividerEnd!=None:
        h1=h1.split(source.h1SectionDividerEnd)[0]
    for delim in source.h1DelStart:
        h1=h1.split(delim)[1]
    h1=h1.split(source.h1DelEnd)[0]
    if '.com' not in h1:
        h1=source.url+h1
    h1s.append(h1)

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
            x=source.url+x
        h2s.append(x)
    


    
    '''
    h2=content.split(source.h2SectionDividerStart, 1)[1]
    h2=h2.split(source.h2SectionDividerEnd, 1)[0]
    
    if source.h2DelStart!=[]:
        while True:
            x=h2
            for delim in source.h2DelStart:
                if delim in h2:
                    x=h2.split(delim)[1]
            x=x.split(source.h2DelEnd)[0]
            if '.com' not in x:
                x=source.url+x
            if x not in h2s:
                h2s.append(x)
                print(x)
            h2=h2.split(source.h2DelStart[0], 1)
            if(len(h2)==1):
                break
            else:
                h2=h2[1]#:][0]



    h2s=splitHTML(content,
                  source.h2SectionDividerStart,
                  source.h2SectionDividerEnd,
                  source.h2DelStart,
                  source.h2DelEnd)

    if source.h2SectionDividerStart!=None:
        h2=h2.split(source.h2SectionDividerStart)[1]
    if source.h2SectionDividerEnd!=None:
        h2=h2.split(source.h2SectionDividerEnd)[0]

    delim0=source.h2DelStart[0]
    while delim0 in h2:
        for delim in source.h2DelStart:
            url=h2.split(delim)[1]
            h2=''.join(h2.split(delim)[1:])
        url=h2.split(source.h2DelEnd)[0]
        h2=h2.split(source.h2DelEnd)[1]
        if '.com' not in url:
            url=source.url+url
        h2s.append(url)
    print(len(h2s))

    h3s=splitHTML(content,
                  source.h3SectionDividerStart,
                  source.h3SectionDividerEnd,
                  source.h3DelStart,
                  source.h3DelEnd)
    '''

    return h1s, h2s, h3s


def buildOutput(newsSourceArr):
    #read in the template html file
    f=open('html_template/template.html', 'r')
    template=f.read()
    f.close()
    
    #set the random order for sources
    h1RandomSources=random.sample(range(len(newsSourceArr)), 4)
    h2RandomSources=random.sample(range(len(newsSourceArr)), 4)
    '''
    print(h3RandomSources)
    h2RandomSources=random.sample(range(len(newsSourceArr)), 1)
    print(h3RandomSources)
    '''

    #replace html template locations with data from newsSourceArr
    for i in range(len(h1RandomSources)):
        source=newsSourceArr[h1RandomSources[i]]
        randomArticle=random.sample(range(len(source.h1Arr)), 1)[0]
        article=source.h1Arr[randomArticle]
        template=template.replace('xxURL1-'+str(i+1)+'xx', article.url)
        template=template.replace('xxTitle1-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg1-'+str(i+1)+'xx', article.img)


    for i in range(len(h2RandomSources)):
        source=newsSourceArr[h2RandomSources[i]]
        print(source.name)
        randomArticle=random.sample(range(len(source.h2Arr)), 1)[0]
        article=source.h2Arr[randomArticle]
        template=template.replace('xxURL2-'+str(i+1)+'xx', article.url)
        template=template.replace('xxTitle2-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg2-'+str(i+1)+'xx', article.img)

    sourcesStr=''
    for i in range(len(newsSourceArr)-1):
        sourcesStr+=newsSourceArr[i].name+', '
    sourcesStr+=newsSourceArr[-1].name
    print(sourcesStr)
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
    for i in range(len(sourceList)):
        source=sourceList[i]
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
        for url in h1s:
            article=buildArticle(url, source.name)
            source.addArticle(article, 1) #sourceList[i].h1Arr.append(article)
        for url in h2s:
            article=buildArticle(url, source.name)
            sourceList[i].h2Arr.append(article)
        for url in h3s:
            article=buildArticle(url, source.name)
            sourceList[i].h3Arr.append(article)
        
    #return the original sourceList,
    #since everything should have been modified in place
    return sourceList        
