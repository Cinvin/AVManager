from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper
from crawler import DBHelper
from model import Genre

adult_cookies={'wei6H':'1','_gat_contentsfc2.embed':'1','_gat_search':'1'}

def spider_movielist(pageindex=1):
    #https://adult.contents.fc2.com/search/?type=1&page=2
    for pageindex in range(1,35):
        #https://adult.contents.fc2.com/search/?type=1&sort=date&order=desc&page=5000
        url=f'https://adult.contents.fc2.com/search/?type=1&sort=date&order=desc&page={pageindex}'
        print(f'pageurl:{url}')
        html = CrawlerHelper.get_requests(url,cookies=adult_cookies).text
        bs = BeautifulSoup(html, "html.parser")
        videos = bs.find_all('div', class_='c-cntCard-110-f')
        for video in videos:
            id = re.findall('/article/(.*?)/',video.find('a')['href'])[0]
            hearttag = video.find('span',class_='c-cntCard-110-f_heart')
            if not hearttag:
                continue
            heart=int(hearttag.get_text().replace(',',''))
            # 只获取收藏量>100的视频
            if heart>=100 and not DBHelper.check_dvdid_exist(f'FC2-PPV-{id}'):
                crawler_videopage(id)
        # if len(re.findall(f'&page={pageindex+1}', html))>0:
        #     pageindex+=1
        # else:
        #     break

def crawler_videopage(id):
    url=f'https://adult.contents.fc2.com/article/{id}/'
    print(url)
    html = CrawlerHelper.get_requests(url,cookies=adult_cookies).text
    bs = BeautifulSoup(html, "html.parser")
    items_article_headerInfo=bs.find('div',class_='items_article_headerInfo')
    if not items_article_headerInfo:
        #非常抱歉，此商品未在您的居住国家公开
        return
    attrs={'href':'/sub_top.php?m=video','aria-selected':'true'}
    if not bs.find('a',attrs):
        return
    title=items_article_headerInfo.find('h3').get_text()
    salertag = bs.find('a', href=re.compile('/users/'))
    if not salertag:
        salertag = bs.find('a', href=re.compile('search/\?author_id='))
    saler=salertag.get_text()
    lenarr=bs.find('p',class_='items_article_info').get_text().split(':')
    length=None
    if len(lenarr)==3:
        length=int(lenarr[0])*60+int(lenarr[1])
    elif len(lenarr)==2:
        length=int(lenarr[0])
    else:
        length=None
    rdate=bs.find('div',class_='items_article_Releasedate').get_text().replace('販売日 : ','')
    items_article_MainitemThumb = bs.find('div',class_='items_article_MainitemThumb')
    picsrc=items_article_MainitemThumb.find('img')['src']
    #https://contents-thumbnail2.fc2.com/w276/storage31000.contents.fc2.com/file/378/37746806/1630302401.84.50.39.png
    piccode=re.findall('storage(.*?).contents',picsrc)[0]+':'+re.findall('/file/(.*?)$',picsrc)[0]
    items_article_SampleImages = bs.find('section',class_='items_article_SampleImages')
    piccount=0
    if items_article_SampleImages:
        smpictags=items_article_SampleImages.find_all('img')
        piccount=len(smpictags)
        if piccount>0:
            piccount=0
            piccode=piccode+' '
            for smpictag in smpictags:
                src=smpictag['src']
                part1=re.findall('storage(.*?).contents',src)
                part2=re.findall('/file/(.*?)$',src)
                if len((part1)) and len(part2):
                    piccount+=1
                    piccode=piccode+part1[0]+':'+part2[0]+','
            piccode=piccode.strip(',')

    genrelist = []
    items_article_TagArea=bs.find('section',class_='items_article_TagArea')
    if items_article_TagArea:
        tags=items_article_TagArea.find_all('a',class_='tagTag')
        for tag in tags:
            genrename=tag.get_text()
            if DBHelper.session.query(Genre).filter(Genre.name_ja==genrename).first():
                genrelist.append(genrename)

    cid=None
    source=10
    code=f'FC2-PPV-{id}'
    print(f"cid:{cid}")
    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    print(f'saler:{saler}')
    #print(f'director:{director}')
    #print(f'studio:{studio}')
    #print(f'label:{label}')
    #print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount}')
    print(genrelist)
    DBHelper.save_movie(code=code, category=3,cid=cid, title=title, length=length, rdate=rdate,
                        studio=saler, label=None,
                        piccode=piccode, piccount=piccount, source=10,genrelist=genrelist)



if __name__ == '__main__':
    spider_movielist()
    #crawler_videopage(2101993)