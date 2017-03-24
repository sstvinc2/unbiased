from unbiasedObjects import *
import os
import random
import time
import re


#take in a url and delimiters, return twitter card
def buildArticle(url, sourceName, encoding=None):#, titleDelStart, titleDelEnd, imgDelStart, imgDelEnd):

    debugging=False
    if debugging:
        print(sourceName)
        print(url)
        print()
    
    #download url
    os.system('wget -q -O scratch/temp_article.html --no-check-certificate '+url)

    #read the file in
    f=open('scratch/temp_article.html', 'r', encoding="utf8")
    content=f.read()
    f.close()

    try:
        if sourceName=='The Guardian':
            #The Guardian puts an identifying banner on their og:images
            #grab the main image from the page instead

            #scenario 1: regular image
            if '<img class="maxed' in content:
                img=content.split('<img class="maxed', 1)[1]
                img=img.split('src="', 1)[1].split('"')[0]
            #scenario 2: video in image spot
            elif '<meta itemprop="image"' in content:
                img=content.split('<meta itemprop="image"', 1)[1]
                img=img.split('content="', 1)[1].split('"')[0]
            #scenario 3: photo essays
            elif '<img class="immersive-main-media__media"' in content:
                img=content.split('<img class="immersive-main-media__media"', 1)[1]
                img=img.split('src="', 1)[1].split('"')[0]
            
        else:
            if 'og:image' in content:
                img=content.split('og:image" content=')[1][1:].split('>')[0]
            elif sourceName=='ABC News':
                img='https://c1.staticflickr.com/7/6042/6276688407_12900948a2_b.jpgX'
            if img[-1]=='/':
                #because the quote separator could be ' or ", 
                #trim to just before it then lop it off
                img=img[:-1].strip()
            img=img[:-1]

        if debugging:
            print(img)

        title=content.split('og:title" content=')[1][1:].split('>')[0]
        if title[-1]=='/':
            title=title[:-1].strip()
        title=title[:-1]

        if debugging:
            print(title)


        author=''
        if sourceName=='The Blaze':
            if 'class="article-author">' in content:
                author=content.split('class="article-author">')[1].split('<')[0]
            elif 'class="article-author" href="' in content:
                author=content.split('class="article-author" href="')[1]
                author=author.split('>')[1].split('<')[0].strip()
        else:
            authorTags=['article:author', 'dc.creator', 'property="author']
            for tag in authorTags:
                if tag in content:
                    author=content.split(tag+'" content=')[1][1:].split('>')[0]
                    author=author[:-1]
                    #trim an extra quotation mark for The Hill
                    if sourceName=='The Hill':
                        author=author.split('"', 1)[0]
                    break

        if debugging:
            print(author)


        if 'og:description' in content:
            description=content.split('og:description" content=')[1][1:].split('>')[0]
            if description[-1]=='/':
                description=description[:-1].strip()
            description=description[:-1]
        else:
            if sourceName=='The Hill':
                description=content.split('div class="field-items"')[-1]
                description=re.sub('<[^<]+?>', '', description)
                description=description[1:200]
            else:
                print("SHOULDN'T GET HERE")

        #strip out self-references
        description=description.replace(sourceName+"'s", '***')
        description=description.replace(sourceName+"'", '***')
        description=description.replace(sourceName, '***')

        if debugging:
            print(description)


        a=Article(title, url, img, description, sourceName, author)
        return a

    except:
        print('^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('\tARTICLE PARSING ERROR')
        print('SOURCE: '+sourceName)
        print('URL: \t'+url)
        print('^^^^^^^^^^^^^^^^^^^^^^^^^ \n\n')
        return None


def buildOutput(newsSourceArr):
    #read in the template html file
    f=open('html_template/template.html', 'r')
    template=f.read()
    f.close()
    
    #set the random order for sources
    h1RandomSources=[]
    while len(h1RandomSources)<4:
        x=random.sample(range(len(newsSourceArr)), 1)[0]
        if len(newsSourceArr[x].h1Arr)>0:
            if x not in h1RandomSources:
                h1RandomSources.append(x)
        else:
            print('\n\n@@@@\nNo H1 stories in '+newsSourceArr[x].name+'\n@@@@\n\n')
    
    #For h2s and h3s, select N random sources (can repeat), then
    #a non-repetitive random article from within 
    h2RandomPairs=[]
    while len(h2RandomPairs) < 6:
        x=random.sample(range(len(newsSourceArr)), 1)[0]
        if len(newsSourceArr[x].h2Arr) > 0:
            y=random.sample(range(len(newsSourceArr[x].h2Arr)), 1)[0]
            pair=[x,y]
            if not pair in h2RandomPairs:
                h2RandomPairs.append(pair)
        else:
            print('\n\n@@@@\nNo H2 stories in '+newsSourceArr[x].name+'\n@@@@\n\n')

    h3RandomPairs=[]
    while len(h3RandomPairs) < 12:
        x=random.sample(range(len(newsSourceArr)), 1)[0]
        print(newsSourceArr[x].name)
        if len(newsSourceArr[x].h3Arr) > 0:
            y=random.sample(range(len(newsSourceArr[x].h3Arr)), 1)[0]
            pair=[x,y]
            if not pair in h3RandomPairs:
                h3RandomPairs.append(pair)
        else:
            print('\n\n@@@@\nNo H3 stories in '+newsSourceArr[x].name+'\n@@@@\n\n')

    #replace html template locations with data from newsSourceArr
    for i in range(len(h1RandomSources)):
        source=newsSourceArr[h1RandomSources[i]]
        randomArticle=random.sample(range(len(source.h1Arr)), 1)[0]
        article=source.h1Arr[randomArticle]
        template=template.replace('xxURL1-'+str(i+1)+'xx', article.url)
        template=template.replace('xxTitle1-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg1-'+str(i+1)+'xx', article.img)
        desc=article.description
        if len(desc)>144:
            desc=desc[:141]
            desc=desc.split()[:-1]
            desc=' '.join(desc)+' ...'
        template=template.replace('xxDesc1-'+str(i+1)+'xx', desc)

    for i in range(len(h2RandomPairs)):
        pair=h2RandomPairs[i]
        article=newsSourceArr[pair[0]].h2Arr[pair[1]]
        template=template.replace('xxURL2-'+str(i+1)+'xx', article.url)
        template=template.replace('xxTitle2-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg2-'+str(i+1)+'xx', article.img)

    for i in range(len(h3RandomPairs)):
        pair=h3RandomPairs[i]
        article=newsSourceArr[pair[0]].h3Arr[pair[1]]
        template=template.replace('xxURL3-'+str(i+1)+'xx', article.url)
        template=template.replace('xxTitle3-'+str(i+1)+'xx', article.title)
        template=template.replace('xxImg3-'+str(i+1)+'xx', article.img)


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
