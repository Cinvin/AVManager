from bs4 import BeautifulSoup
import re
import sqlhelper
from crawler import CrawlerHelper, DBHelper, Tools
from crawler.shop.fanza_amateur import crawler_dmm_amateur_page
#https://av-wiki.net/mgstage/
#https://av-wiki.net/fanza-shirouto/

def pagelist(maxpage=None):
    pageindex=1
    while True:
        pageurl=f'https://avdanyuwiki.com/%e5%85%a8%e4%bd%9c%e5%93%81%e4%b8%80%e8%a6%a7/page/{pageindex}/'
        print(pageurl)
        response=CrawlerHelper.get_requests(pageurl)
        response.encoding='utf-8'
        html=response.text
        bs = BeautifulSoup(html, "html.parser")
        articles=bs.find_all(name='article',class_=re.compile('post-(\d*?)'))
        for article in articles:
            #href="https://www.mgstage.com/product/product_detail/200GANA-2490/?aff=QTWJYS6BP24YCHBPG2PDC83284"
            categories=article.find(class_='post-categories')
            if not categories:
                continue
            category=categories.get_text().strip()
            cid=re.findall('品番：[\s]*([^\s]*?)[\s]', article.get_text())
            if len(cid)==0:
                continue
            cid=cid[0]
            histrionlist=[]
            histrionobjs=article.find_all('a',href=re.compile('https://avdanyuwiki.com/tag/(.*?)/'))
            for histrionobj in histrionobjs:
                histrion_name=histrionobj.get_text()
                if histrion_name=='黒人' or histrion_name=='素人' or '主観' in histrion_name or '?' in histrion_name:
                    continue
                histrionlist.append(histrion_name)
            if len(histrionlist)==0:
                continue
            source=1
            if 'MGS' in category:
                source=2
            else:
                sqlres = sqlhelper.fetchone('select id,cid from t_av where piccode=%s and source=1', cid)
                if not sqlres:
                    continue
                cid = sqlres['cid']
            print(cid,histrionlist)
            DBHelper.save_movie_histrion(cid,source,histrionlist)
        if maxpage and maxpage == pageindex:
            break
        if bs.find('a',href=re.compile(f'/page/{pageindex+1}')):
            pageindex+=1
        else:
            break

if __name__ == '__main__':
    pagelist()
