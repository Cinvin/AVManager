import json
import string

import requests
from bs4 import BeautifulSoup
import re

import sqlhelper
from crawler import CrawlerHelper
from datetime import datetime
from time import sleep
import sys
from crawler import DBHelper

sys.path.append("..")
import gzip

# setting
freq = 2 # second

#sitemap: https://www.mgstage.com/product_detail_sitemap1.xml.gz

def spider_by_sitemap(freq:int=freq):
    sitemapurl='https://www.mgstage.com/product_detail_sitemap{num}.xml.gz'
    for i in range(1,4):
        print(f'crawler sitemap page {str(i)}')
        data = CrawlerHelper.get_requests(sitemapurl.replace("{num}", str(i)))
        data = gzip.decompress(data.content).decode('utf8')
        bs = BeautifulSoup(data, "xml")
        links = bs.find_all("loc")
        del data
        del bs
        for link in links:
            url=link.get_text()
            piccode = re.findall('/product/product_detail/(.*?)/', url)[0]
            code=getcode_by_piccode_mgstage(piccode)
            if not DBHelper.check_dvdid_exist(code):
                spider_moviePage(link.get_text())
                sleep(freq)

def spider_by_maker(freq:int):
    sitemapurl='https://www.mgstage.com/maker_sitemap.xml.gz'
    data = CrawlerHelper.get_requests(sitemapurl)
    data = gzip.decompress(data.content).decode('utf8')
    bs = BeautifulSoup(data, "xml")
    links = bs.find_all("loc")
    idx = 45
    links = links[idx:]
    #独占
    link = ['https://www.mgstage.com/search/cSearch.php?search_word=&maker[]=Jackson_0&sort=new&list_cnt=120&type=top',
            ]
    del data
    del bs
    for link in links:
        link=link.get_text()
        urlbase = link+'&page={page}'
        pageindex=1
        idx=idx+1
        while 1==1:
            url=urlbase.replace('{page}',str(pageindex))
            html = gethtml(url)
            bs = BeautifulSoup(html, "html.parser")
            studio=bs.find('input',class_='b_image_word_ids')["value"][:-2]
            print(f"studio:{studio} page:{pageindex} {idx}")

            mgscode = re.findall(f'https://image.mgstage.com/images/(.*?)/', html)
            if len(mgscode) > 0:
                DBHelper.save_mgscode(studio, mgscode[0])

            linktags=bs.find_all('a', href=re.compile('/product/product_detail/'))
            for linktag in linktags:
                titletag=linktag.find('p')
                if titletag is None:
                    continue
                url = linktag["href"]
                title = titletag.get_text().split(' ')[0]
                title = title_transfrom(title)
                cid = re.findall('/product/product_detail/(.*?)/',url)[0]
                code=getcode_by_piccode_mgstage(cid)
                avitem=DBHelper.get_movie_by_cid(2,cid)
                if not avitem:
                    avitem=DBHelper.get_movie_obj(code,studio)
                if avitem:
                    continue
                if not DBHelper.check_movie_exist_with_title_similar(code,title):
                    spider_moviePage('https://www.mgstage.com'+url)
                    #sleep(freq)
            if len(linktags)==0:
                break
            pageindex=1+pageindex
            sleep(freq)
        sleep(freq)

def spider_newrelease():
    for pageindex in range(1, 30):# maxpage:84
        listurl = f'https://www.mgstage.com/search/cSearch.php?search_word=&sort=new&list_cnt=120&type=top&page={pageindex}'
        html = gethtml(listurl)
        bs = BeautifulSoup(html, "html.parser")
        linktags = bs.find_all('a', href=re.compile('/product/product_detail/'))
        for linktag in linktags:
            titletag = linktag.find('p')
            if titletag is None:
                continue
            url = linktag["href"]
            title = titletag.get_text().split(' ')[0]
            title = title_transfrom(title)
            cid = re.findall('/product/product_detail/(.*?)/', url)[0]
            code = getcode_by_piccode_mgstage(cid)
            avitem = DBHelper.get_movie_by_cid(2, cid)
            if avitem:
                continue
            if not DBHelper.check_dvdid_exist(code):
                spider_moviePage('https://www.mgstage.com' + url)
                # sleep(freq)
        if len(linktags) == 0:
            break

def spider_reservation():
    pageindex = 1
    while True:
        listurl = f'https://www.mgstage.com/search/cSearch.php?sort=popular&list_cnt=120&range=reservation&type=top&page={pageindex}'
        html = gethtml(listurl)
        bs = BeautifulSoup(html, "html.parser")
        linktags = bs.find_all('a', href=re.compile('/product/product_detail/'))
        for linktag in linktags:
            titletag = linktag.find('p')
            if titletag is None:
                continue
            url = linktag["href"]
            title = titletag.get_text().split(' ')[0]
            title = title_transfrom(title)
            cid = re.findall('/product/product_detail/(.*?)/', url)[0]
            code = getcode_by_piccode_mgstage(cid)
            avitem = DBHelper.get_movie_by_cid(2, cid)
            if avitem:
                continue
            if not DBHelper.check_dvdid_exist(code):
                spider_moviePage('https://www.mgstage.com' + url)
                # sleep(freq)
        if len(linktags) == 0:
            break
        pageindex=pageindex+1

#https://www.mgstage.com/product/product_detail/022SGSR-079/
def spider_moviePage(url):
    response = CrawlerHelper.get_requests(url, cookies={'adc':'1'})
    if response.url=='https://www.mgstage.com/':
        return

    html = gethtml(url)
    if len(html) == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 内容为空{url}")
        return
    bs = BeautifulSoup(html, "html.parser")
    # 标题

    title = bs.find("h1",class_="tag")
    if title:
        title = title.get_text().strip()
    else:
        title = bs.find("title").get_text().strip()
        title = re.findall('「(.*)」',title)[0]

    title=title_transfrom(title)

    # piccode=bs.find_all('img',class_='enlarge_image')[0]['src']
    # piccode=piccode.lstrip('https://image.mgstage.com/images/').rstrip('.jpg')
    # piccode=piccode.replace('/pf_o1_','/*_').replace('/pb_p_', '/*_')
    piccode=re.findall('https://www.mgstage.com/product/product_detail/(.*?)/',url)[0]

    code = None
    rdate = None
    rdate2 = None
    length = None
    director = None
    studio = None
    label = None
    series = None
    actslist = []
    genrelist =[]
    trs=bs.find_all("tr")
    for tr in trs:
        tkey = tr.find_all("th")
        if len(tkey)>0:
            tkey=tkey[0].get_text()
        else:
            continue
        tval = tr.find_all("td")
        if len(tval) == 0:
            continue
        tval=tval[0]
        if tkey == '品番：':
            code=tval.get_text().strip()
            code = getcode_by_piccode_mgstage(code)

        elif tkey == '出演：':
            acttags = tval.find_all('a')
            for acttag in acttags:
                actname=acttag.get_text().strip()
                actimgurl=f'https://static.mgstage.com/mgs/img/common/actress/{actname}.jpg'
                if bs.find('img',src=actimgurl) and not sqlhelper.fetchone('select 1 from t_actress where actname=%s',actname):
                    if requests.head(actimgurl).status_code==200:
                        sqlhelper.execute('insert into t_actress(actname,avatar) values(%s,%s)',actname,actimgurl)
                    #insert into javlibrary_maker(studio_code,studio_name) values(%s,%s)
                actslist.append(acttag.get_text().strip())
        elif tkey == 'メーカー：':
            studio=tval.get_text().strip()
            studio=studio_transfrom(studio)
        elif tkey == '収録時間：':
            length = tval.get_text().rstrip('min')
        elif tkey == '商品発売日：':
            rdate = tval.get_text()
            if rdate=='DVD未発売':
                rdate=None
        elif tkey == '配信開始日：':
            rdate2 = tval.get_text()
        elif tkey == 'シリーズ：':
            series = tval.get_text().strip()
            if series=='': series=None
        elif tkey == 'レーベル：':
            label = tval.get_text().strip()
            label = label_transfrom(label)
            if label=='': label=None
        elif tkey == 'ジャンル：':
            genretags=tval.find_all('a')
            for tag in genretags:
                genre = tag.get_text().strip()
                if len(genre) > 0:
                    genrelist.append(genre)

    if rdate is None and rdate2 is not None and rdate2 != 'DVD未発売':
        rdate=rdate2

    pics=bs.find_all('img', src=re.compile('/cap_'))
    piccount=len(pics)

    videocode=None
    video=bs.find_all('a',href=re.compile('/sampleplayer/sampleplayer.html/(.*?)$'))
    if len(video):
        pid=re.findall('/sampleplayer/sampleplayer.html/(.*?)$',video[0]['href'])[0]
        videores=gethtml(f'https://www.mgstage.com/sampleplayer/sampleRespons.php?pid={pid}')
        resultobj = json.loads(videores)
        videocode = re.findall(f'{piccode.replace("-","/").lower()}/(.*?)\.ism', resultobj["url"])
        if len(videocode):
            videocode=videocode[0]
        else:
            videocode=None

    DBHelper.save_movie(code=code, cid=piccode, title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=videocode, piccount=piccount, source=2,
                        actresslist=actslist, genrelist=genrelist)

    # https://image.mgstage.com/images/(.*?)/300maan/001/pb_e_300maan-001.jpg
    mgscode = re.findall(f'https://image.mgstage.com/images/(.*?)/{ piccode.lower().replace("-","/") }/', html)
    if len(mgscode)>0:
        DBHelper.save_mgscode(studio,mgscode[0])

def getcode_by_piccode_mgstage(piccode):
    if len(piccode)<3:
        return piccode
    is_makerstart=True
    for i in range(0,3):
        if piccode[i] not in string.digits:
            is_makerstart=False
            break
    if is_makerstart:
        return piccode[3:]
    return piccode

def gethtml(url):
    html = CrawlerHelper.get_requests(url, cookies={'adc': '1'})
    if html is None:
        sleep(freq)
        html = CrawlerHelper.get_requests(url, cookies={'adc': '1'})
    if html is None:
        return None
    if html.status_code != 200:
        raise Exception(f'{html.status_code} 请检查 {url}')
    return html.text

def studio_transfrom(studio):
    if studio=='Mellow Moon':
        return 'Mellow Moon（メロウムーン）'
    elif studio=='GOLDENCANDY':
        return 'golden Candy'
    return studio

def label_transfrom(label):
    return label

def title_transfrom(title):
    c1 = re.compile(f'【MGSだけのおまけ映像付き\+(\d*)分】')  # 【MGSだけのおまけ映像付き+20分】
    title = c1.sub('', title)
    title = title.replace('【期間限定販売】', '')
    title = title.replace('【MGS独占配信BEST】', '')
    title = title.replace('【初回限定版 特典映像付き】','')
    title = title.strip()
    return title

if __name__ == '__main__':
    spider_newrelease()
    #spider_reservation()
    spider_by_sitemap(freq=freq)
    #spider_by_maker(freq=freq)