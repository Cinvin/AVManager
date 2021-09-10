from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper,DBHelper
from crawler.shop import ave
from time import sleep

# setting
freq = 0.5 # second

def spider_sitemap():
    xmlurl = f"https://www.caribbeancom.com/static-seo/sitemap-videos.xml"
    html = CrawlerHelper.get_requests(xmlurl)
    bs = BeautifulSoup(html.text, "xml")
    urltags = bs.find_all("url")
    for urltag in urltags:
        loc=urltag.find('loc').contents[0]
        findcode=re.findall('https://www.caribbeancom.com/moviepages/(.*?)/', loc)
        if len(findcode)==0:
            continue
        code=findcode[0]
        if DBHelper.get_movie_obj(code,'カリビアンコム'):
            continue

        video=urltag.find('video:video')
        video_content_loc=video.content_loc.get_text()
        videog=None
        if len(video_content_loc)>0:
            videog=re.findall(code+'/(.*?).mp4',video_content_loc)[0]
        actinfo=video.tag.get_text()
        title=video.title.get_text().split('|')[0]
        title=title.replace(actinfo,'',1).strip()
        rdate=video.publication_date.get_text()
        length=int(video.duration.get_text())//60
        tags=video.find_all('tag')
        actresslist=actinfo.split(' ')
        if '---' in actresslist:
            actresslist.remove('---')
        genrelist=[tag.get_text() for tag in tags[1:]]
        print(code)
        print(title)
        print(length)
        print(rdate)
        print(actresslist)
        print(genrelist)
        print(videog)
        DBHelper.save_movie(code=code, category=2,cid=None, title=title, length=length, rdate=rdate,
                            director=None, studio='カリビアンコム'
        , label=None, series=None,
                            piccode=videog, piccount=0, source=1006,
                            actresslist=actresslist, genrelist=genrelist)


if __name__=='__main__':
    spider_sitemap()