from datetime import datetime,timedelta
import gzip
import re

from sqlalchemy import or_

import sqlhelper
from crawler import Tools, DBHelper,CrawlerHelper
from bs4 import BeautifulSoup
from model import *
from concurrent.futures import ThreadPoolExecutor, as_completed

dmmcookie={'age_check_done':'1'}

def crawler_dmmmoive(cid):
    url=f'https://www.dmm.co.jp/digital/videoa/-/detail/=/cid={cid}/'
    html=CrawlerHelper.get_requests(url,cookies=dmmcookie)
    if html==None:
        print(f'error:{cid}')
        return
    if html.status_code==404:
        print(f'404:{cid}')
        return
    print(f'{cid} start')
    html=html.text
    bs = BeautifulSoup(html, "html.parser")

    title=bs.find('h1',id='title').get_text()
    title=Tools.dmm_title_transform(title)

    rdate = None
    rdatefind = re.findall('商品発売日：</td>[\s]*<td>[\s]*(.*?)[\s]*</td>[\s]*</tr>',
                       html)
    if len(rdatefind) == 0 or rdatefind[0] == '----':
        rdatefind = re.findall( '配信開始日：</td>[\s]*<td>[\s]*(.*?)[\s]*</td>[\s]*</tr>', html)
    if len(rdatefind) == 0:
        rdatefind = re.findall( '配信開始日：</td>[\s]*<td valign="top">[\s]*(.*?)[\s]*</td>[\s]*</tr>', html)
    if len(rdatefind) > 0 and rdatefind[0] != '----':
        rdate = rdatefind[0]
        if len(rdate) > 10:
            rdate = rdate[0:10]
    length=re.findall('<td align="right" valign="top" class="nw">収録時間：</td>[\s]*<td>[\s]*(.*?)分[\s]*</td>[\s]*</tr>',html)
    if len(length) > 0:
        length = length[0]
    else:
        length = None
    piccode = \
    re.findall('<td align="right" valign="top" class="nw">品番：</td>[\s]*<td>[\s]*(.*?)[\s]*</td>[\s]*</tr>', html)[0]
    if piccode == '----':
        piccode = None

    code = Tools.get_dvdid(cid,piccode,1)


    director=None
    dicttemp = {'data-i3pst': "info_director"}
    directortag=bs.find('a',dicttemp)
    if directortag:
        director=directortag.get_text()

    studio=None
    dicttemp = {'data-i3pst': "info_maker"}
    studiotag=bs.find('a',dicttemp)
    if studiotag:
        studio=studiotag.get_text().strip()
        studio_fanzaid = re.findall('/article=maker/id=(\d*)/', studiotag['href'])
        if len(studio_fanzaid) > 0:
            studio_fanzaid = studio_fanzaid[0]
            if len(studio_fanzaid) > 0 and len(studio) > 0:
                DBHelper.save_studio_fanzaid(studio,studio_fanzaid)

    label = None
    dicttemp = {'data-i3pst': "info_label"}
    labeltag = bs.find('a', dicttemp)
    if labeltag:
        label = labeltag.get_text()

    series = None
    dicttemp = {'data-i3pst': "info_series"}
    seriestag = bs.find('a', dicttemp)
    if seriestag:
        series = seriestag.get_text()

    piccount=0
    picdiv = bs.find(id='sample-image-block')
    if picdiv:
        piccount=len(picdiv.find_all('img'))

    actslist=[]
    histrionlist=[]
    findactajax=re.findall('/digital/videoa/-/detail/ajax-performer/=/data=(.*?)/',html)
    bsact=bs
    if len(findactajax)>0:
        actajaxhtml=CrawlerHelper.get_requests(f'https://www.dmm.co.jp/digital/videoa/-/detail/ajax-performer/=/data={findactajax[0]}/',cookies=dmmcookie)
        bsact=BeautifulSoup(actajaxhtml.text, "html.parser")
    dicttemp = {'data-i3pst': "info_actress"}
    actstags = bsact.find_all('a', dicttemp)
    for actstag in actstags:
        actname=actstag.get_text()
        actid = re.findall('/id=(.*?)/', actstag['href'])[0]

        if 'actress' in actstag['href']:
            dbactname = DBHelper.get_actname_by_fanzaid(actid)
            if dbactname:
                actname = dbactname
            else:
                DBHelper.save_actress_fanzaid(actname, actid)
            actslist.append(actname)
        elif 'histrion' in actstag['href']:
            histrionlist.append(actname)
            DBHelper.save_histrion_fanzaid(actname, actid)
    genrelist = []
    dicttemp={'data-i3pst':"info_genre"}
    genretags = bs.find_all('a',dicttemp)
    for genretag in genretags:
        genrelist.append(genretag.get_text())
    print(f"cid:{cid}")
    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    print(f'director:{director}')
    print(f'studio:{studio}')
    print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount}')
    print(actslist)
    print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code,cid=cid,title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=piccount, source=1,
                        actresslist=actslist, genrelist=genrelist,histrionlist=histrionlist)

def spider_by_sitemap():
    url='https://www.dmm.co.jp/digital/sitemap_index.xml'
    xml=CrawlerHelper.get_requests(url)
    bs = BeautifulSoup(xml.text, "xml")
    sitemaplinks = bs.find_all("loc")

    for sitemaplink in sitemaplinks:
        sl=sitemaplink.get_text()
        findxml=re.findall('https://www.dmm.co.jp/digital/sitemap_videoa_(\d*).xml.gz',sl)
        if len(findxml)>0:
            data=CrawlerHelper.get_requests(sl)
            data = gzip.decompress(data.content).decode('utf8')
            videoabs = BeautifulSoup(data, "xml")
            urls = videoabs.find_all("url")
            del data
            del videoabs
            while len(urls)>0:
                urlitem=urls.pop()
                loc=urlitem.loc
                video=urlitem.video
                if not loc:
                    continue
                loc=loc.get_text()
                cid = re.findall('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=(.*?)/', loc)[0]
                title=None
                rdate=None
                if video:
                    publication_date = video.publication_date.get_text()[0:10]
                    expiration_date = video.expiration_date.get_text()[0:10]
                    rdate=publication_date
                    if rdate == '2038-01-01':
                        rdate=expiration_date
                    if rdate == '2038-01-01':
                        rdate = None
                    if rdate:
                        rdate=datetime.fromisoformat(rdate)
                avitem = DBHelper.get_movie_by_cid(1, cid)
                if not avitem:
                    crawler_dmmmoive(cid)
                else:
                    if avitem.piccount==0 and avitem.rdate>datetime.now()-timedelta(days=30):
                        crawler_dmmmoive(cid)
                    elif not avitem.rdate:
                        crawler_dmmmoive(cid)

def spider_newrelease():
    for pageindex in range(1,31):# maxpage:417
        dvdlisturl = f'https://www.dmm.co.jp/digital/videoa/-/list/=/sort=date/page={pageindex}/'
        html = CrawlerHelper.get_requests(dvdlisturl, cookies=dmmcookie)
        if not html or html.status_code == 404:
            return
        bs = BeautifulSoup(html.text, "html.parser")
        dvdurls = bs.find_all('a', href=re.compile('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid='))
        for dvdurl in dvdurls:
            cid = re.findall('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=(.*?)/', dvdurl['href'])[0]
            avitem = DBHelper.get_movie_by_cid(1, cid)
            if not avitem:
                crawler_dmmmoive(cid)
            else:
                if avitem.piccount == 0 and avitem.rdate > datetime.now() - timedelta(days=30):
                    crawler_dmmmoive(cid)
                elif not avitem.rdate:
                    crawler_dmmmoive(cid)

def spider_reserve():
    #予約商品
    pageindex = 1
    while True:# maxpage:417
        dvdlisturl = f'https://www.dmm.co.jp/digital/videoa/-/list/=/reserve=only/sort=date/page={pageindex}/'
        html = CrawlerHelper.get_requests(dvdlisturl, cookies=dmmcookie)
        if not html or html.status_code == 404:
            return
        bs = BeautifulSoup(html.text, "html.parser")
        dvdurls = bs.find_all('a', href=re.compile('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid='))
        for dvdurl in dvdurls:
            cid = re.findall('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=(.*?)/', dvdurl['href'])[0]
            avitem = DBHelper.get_movie_by_cid(1, cid)
            if not avitem:
                crawler_dmmmoive(cid)
            else:
                if avitem.piccount == 0:
                    crawler_dmmmoive(cid)
        pageindex+=1
        if not bs.find('a',href=f'/digital/videoa/-/list/=/reserve=only/sort=date/page={pageindex}/'):
            break

if __name__ == '__main__':
    spider_by_sitemap()
    #spider_reserve()
    #spider_newrelease()
