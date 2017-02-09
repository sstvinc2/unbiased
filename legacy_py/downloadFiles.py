import os

files=[]
files.append('http://www.nytimes.com')
files.append('http://www.nbcnews.com')
files.append('http://www.foxnews.com')

stories=[]
stories.append('https://www.nytimes.com/2017/02/03/business/dealbook/trump-congress-financial-regulations.html')
stories.append('http://www.nbcnews.com/news/us-news/over-100-000-visas-have-been-revoked-immigration-ban-justice-n716121')
stories.append('http://www.foxnews.com/politics/2017/02/03/calls-mount-for-trump-administration-to-label-muslim-brotherhood-terrorist-organization.html')

for i in range(len(files)):
    os.system('wget -O source'+str(i+1)+'.html --no-check-certificate '+files[i])
    
for i in range(len(stories)):
    os.system('wget -O story'+str(i+1)+'.html --no-check-certificate '+stories[i])

'''
f=open('testOut.html', 'r', encoding="utf8")
content=f.read()
f.close()
#os.remove('testOut.html')
'''
