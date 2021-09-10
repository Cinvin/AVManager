from bs4 import BeautifulSoup
import re
import sqlhelper
from crawler import CrawlerHelper, DBHelper, Tools
from crawler.shop.fanza_amateur import crawler_dmm_amateur_page
#https://av-wiki.net/mgstage/
#https://av-wiki.net/fanza-shirouto/
def pagelist(url):
    pageindex=100
    while True:
        pageurl=url+f'/page/{pageindex}/'
        print(pageurl)
        response=CrawlerHelper.get_requests(url+f'/page/{pageindex}/')
        response.encoding='utf-8'
        html=response.text
        bs = BeautifulSoup(html, "html.parser")
        articles=bs.find_all(name='article',class_='archive-list-wrap')
        for article in articles:
            #href="https://www.mgstage.com/product/product_detail/200GANA-2490/?aff=QTWJYS6BP24YCHBPG2PDC83284"
            mgstage=article.find('a',href=re.compile('mgstage.com/product/product_detail/(.*?)/'))
            cid=None
            if mgstage:
                cid=re.findall('mgstage.com/product/product_detail/(.*?)/',mgstage['href'])[0]
            fanza_digital = article.find('img', src=re.compile('pics.dmm.co.jp/digital/video/(.*?)/'))
            fanza_amateur = article.find('img',src=re.compile('pics.dmm.co.jp/digital/amateur/(.*?)/'))
            if fanza_digital:
                cid = re.findall('pics.dmm.co.jp/digital/video/(.*?)/', fanza_digital['src'])[0]
            if fanza_amateur:
                print(fanza_amateur['src'])
                cid = re.findall('pics.dmm.co.jp/digital/amateur/(.*?)/',fanza_amateur['src'])[0]

            rdate = None
            haishin_date=article.find('li',class_='haishin-date')
            if haishin_date:
                rdate=haishin_date.get_text().strip()
            else:
                lis=article.find_all('li')
                for li in lis:
                    re_rdate=re.findall('配信開始日：(.*?)$',li.get_text())
                    if len(re_rdate)>0:
                        rdate=re_rdate[0].strip()
                        break
                    re_rdate = re.findall('配信日：(.*?)$', li.get_text())
                    if len(re_rdate) > 0:
                        rdate = re_rdate[0].strip()
                        break
            actresslist=[]
            actressobjs=article.find_all('a',href=re.compile('av-wiki.net/av-actress/(.*?)/'))
            for actressobj in actressobjs:
                if '/unknown/' in actressobj['href'] or actressobj.get_text()=='＊＊＊':
                    continue
                actresslist.append(actressobj.get_text())
            if len(actresslist)==0:
                continue
            source=None
            if fanza_digital:
                source=1
                sqlres=sqlhelper.fetchone('select id,cid from t_av where piccode=%s and source=1',cid)
                if not sqlres:
                    continue
                cid=sqlres['cid']
                sqlres2=sqlhelper.fetchone('select count(1) as c from t_av_actress where av_id=%s',sqlres['id'])
                if len(actresslist)<=sqlres2['c']:
                    continue
            elif mgstage:
                source=2
            elif fanza_amateur:
                source=4
            print(cid)
            print(rdate)
            print(actresslist)
            DBHelper.save_movie_actress(cid,source,actresslist)
        if bs.find('a',href=re.compile(f'/page/{pageindex+1}')):
            pageindex+=1
        else:
            break

if __name__ == '__main__':
    #pagelist('https://av-wiki.net/mgstage')
    pagelist('https://av-wiki.net/fanza-video')
    #pagelist('https://av-wiki.net/fanza-shirouto')

