import gzip
import re

from sqlalchemy import and_

from crawler import Tools, DBHelper, CrawlerHelper
from bs4 import BeautifulSoup

import sqlhelper
from model import AV

dmmcookie={'age_check_done':'1'}

def crawler_dmm_amateur_page(cid):
    url=f'https://www.dmm.co.jp/digital/videoc/-/detail/=/cid={cid}/'
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

    title=bs.find('h1').get_text()
    title=Tools.dmm_title_transform(title)
    #貸出開始日：</td>[\s]*<td>2002/12/16[\s]*<
    '配信開始日：</td>[\s]*<td>[\s]*2021/05/07</td>'
    rdate=re.findall('配信開始日：</td>[\s]*<td>[\s]*(.*?)[\s]*<',html)[0]
    if rdate == '----':
        rdate=None
    '収録時間：</td>[\s]*<td>(.*?)分'
    length=re.findall('収録時間：</td>[\s]*<td>[\s]*(.*?)分[\s]*</td>[\s]*</tr>',html)
    if len(length) > 0:
        length = length[0]
    else:
        length=None
    #品番：</td>[\s]*<td>(.*?)</td>
    piccode=None
    piccodefind = re.findall(f'https://pics.dmm.co.jp/digital/amateur/{cid}/(.*?)jp.jpg', html)
    if len(piccodefind)==0:
        piccodefind = re.findall(f'https://pics.dmm.co.jp/digital/amateur/{cid}/(.*?)js', html)
    if len(piccodefind) > 0:
        piccode=piccodefind[0]
    director = None
    dicttemp = {'data-i3pst': "info_director"}
    directortag = bs.find('a', dicttemp)
    if directortag:
        director = directortag.get_text()

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

    actslist = []
    histrionlist = []
    findactajax = re.findall('/digital/videoa/-/detail/ajax-performer/=/data=(.*?)/', html)
    bsact = bs
    if len(findactajax) > 0:
        actajaxhtml = CrawlerHelper.get_requests(
            f'https://www.dmm.co.jp/digital/videoc/-/detail/ajax-performer/=/data={findactajax[0]}/', cookies=dmmcookie)
        bsact = BeautifulSoup(actajaxhtml.text, "html.parser")
    dicttemp = {'data-i3pst': "info_actress"}
    actstags = bsact.find_all('a', dicttemp)
    for actstag in actstags:
        actname = actstag.get_text()
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

    actslist=[]
    genrelist = []
    dicttemp = {'data-i3pst': "info_genre"}
    genretags = bs.find_all('a', dicttemp)
    for genretag in genretags:
        genrelist.append(genretag.get_text())

    piccount = 0
    picdiv = bs.find(id='sample-image-block')
    if picdiv:
        simgs = picdiv.find_all('img')
        piccount = len(simgs)

    code=Tools.get_dvdid(cid,piccode,3)

    if not studio and label:
        studio=label

    dbcheck = DBHelper.get_movie_obj(code,studio)
    if dbcheck and dbcheck.source == 2:
        DBHelper.delete_movie(dbcheck.id)

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
    print(genrelist)
    DBHelper.save_movie(code=code,cid=cid,title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=piccount, source=4,
                        actresslist=actslist, genrelist=genrelist,histrionlist=histrionlist)

def spider_by_sitemap():
    url='https://www.dmm.co.jp/digital/sitemap_index.xml'
    xml=CrawlerHelper.get_requests(url)
    avs = DBHelper.session.query(AV.cid).filter(and_(AV.source == 4, AV.rdate != None)).all()
    cidlist = [av.cid for av in avs]
    del avs
    bs = BeautifulSoup(xml.text, "xml")
    sitemaplinks = bs.find_all("loc")
    for sitemaplink in sitemaplinks:
        sl=sitemaplink.get_text()
        findxml=re.findall('https://www.dmm.co.jp/digital/sitemap_videoc_(\d*).xml.gz',sl)
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
                cid = re.findall('https://www.dmm.co.jp/digital/videoc/-/detail/=/cid=(.*?)/', loc)[0]
                if cid in cidlist:
                    continue
                title=None
                rdate=None
                if video:
                    rdate=video.publication_date.get_text()[0:10]
                    if rdate=='2038-01-01':
                        rdate=video.expiration_date.get_text()[0:10]
                    if rdate=='2038-01-01':
                        rdate=None
                    title = video.title.get_text()
                crawler_dmm_amateur_page(cid)

def spider_newrelease():
    for pageindex in range(1,31):# maxpage:292
        dvdlisturl = f'https://www.dmm.co.jp/digital/videoc/-/list/=/sort=date/page={pageindex}/'
        html = CrawlerHelper.get_requests(dvdlisturl, cookies=dmmcookie)
        if not html or html.status_code == 404:
            return
        bs = BeautifulSoup(html.text, "html.parser")
        dvdurls = bs.find_all('a', href=re.compile('https://www.dmm.co.jp/digital/videoc/-/detail/=/cid='))
        for dvdurl in dvdurls:
            cid = re.findall('https://www.dmm.co.jp/digital/videoc/-/detail/=/cid=(.*?)/', dvdurl['href'])[0]
            avitem = DBHelper.get_movie_by_cid(4, cid)
            if not avitem:
                crawler_dmm_amateur_page(cid)
if __name__ == '__main__':
    #spider_by_sitemap()
    spider_newrelease()