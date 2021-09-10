import re
import string

from crawler import Tools, DBHelper, CrawlerHelper
from bs4 import BeautifulSoup

dmmcookie={'age_check_done':'1'}

def crawler_dmmdvd_page(cid):
    #https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=2open0616/
    #https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=2open616/
    url=f'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid={cid}/'
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

    rdate=re.findall('発売日：</td>[\s]*<td width="100%">(.*?)</td>',html)[0]
    if rdate == '----':
        rdate=None
    #
    length=re.findall('収録時間：</td>[\s]*<td width="100%">(.*?)分',html)
    if len(length)>0:
        length=length[0]
    else:
        length=None
    piccode = \
    re.findall('品番：</td>[\s]*<td width="100%">(.*?)</td>', html)[0]
    if piccode == '----':
        piccode = ''
    director=None
    directortag=bs.find('a',href=re.compile('/mono/dvd/-/list/=/article=director/'))
    if directortag:
        director=directortag.get_text()

    studio=None
    studiotag=bs.find('a',href=re.compile('/mono/dvd/-/list/=/article=maker/'))
    if studiotag:
        studio=studiotag.get_text().strip()
        studio_fanzaid = re.findall('/article=maker/id=(\d*)/', studiotag['href'])
        if len(studio_fanzaid) > 0:
            studio_fanzaid = studio_fanzaid[0]
            DBHelper.save_studio_fanzaid(studio,studio_fanzaid)

    label = None
    labeltag = bs.find('a',href=re.compile('/mono/dvd/-/list/=/article=label/'))
    if labeltag:
        label = labeltag.get_text()

    series = None
    seriestag = bs.find('a', href=re.compile('/mono/dvd/-/list/=/article=series/'))
    if seriestag:
        series = seriestag.get_text()

    histrionlist=[]
    actslist=[]

    performerbs=bs.find('span',id='performer')

    #'/mono/dvd/-/detail/performer/=/cid=53dv461/'
    findactajax = re.findall('/mono/dvd/-/detail/performer/=/cid=(.*?)/', html)
    if len(findactajax) > 0:
        actajaxhtml = CrawlerHelper.get_requests(
            f'https://www.dmm.co.jp/mono/dvd/-/detail/performer/=/cid={findactajax[0]}/',cookies=dmmcookie)
        performerbs = BeautifulSoup(actajaxhtml.text, "html.parser")

    actstags = performerbs.find_all('a', href=re.compile('/mono/dvd/-/list/=/article=actress/'))
    for actstag in actstags:
        actname=actstag.get_text()
        actid = re.findall('/id=(.*?)/', str(actstag['href']))[0]
        dbactname=DBHelper.get_actname_by_fanzaid(actid)
        if dbactname:
            actname=dbactname
        else:
            DBHelper.save_actress_fanzaid(actname,actid)
        actslist.append(actname)

    actstags = performerbs.find_all('a', href=re.compile('/mono/dvd/-/list/=/article=histrion/'))
    for actstag in actstags:
        actname = actstag.get_text()
        actid = re.findall('/id=(.*?)/', str(actstag['href']))[0]
        DBHelper.save_histrion_fanzaid(actname, actid)
        histrionlist.append(actname)
    genrelist = []
    #ジャンル：</td>(.*?)</tr>
    genrearea=re.findall('ジャンル：</td>[\s]*(.*?)[\s]*</tr>',html)[0]
    bsgenre=BeautifulSoup(genrearea, "html.parser")
    genretags = bsgenre.find_all('a', href=re.compile('/mono/dvd/-/list/=/article=keyword/'))
    for genretag in genretags:
        genrelist.append(genretag.get_text())

    is_update=DBHelper.get_movie_by_cid(3,cid) is not None

    piccount = 0
    picdiv = bs.find(id='sample-image-block')
    if picdiv:
        simgs = picdiv.find_all('img')
        piccount = len(simgs)
        if piccount > 0:
            imgurl = simgs[0]['src']
            # https://pics.dmm.co.jp/digital/video/118bsd00001/118bsd00001-1.jpg
            piccodefind = re.findall('https://pics.dmm.co.jp/digital/video/(.*?)/', imgurl)
            if len(piccodefind) > 0:
                sample = piccodefind[0]
                if sample != piccode:
                    piccode = piccode +' '+ sample
                if not is_update:
                    piccodeav = DBHelper.check_piccode_exist(sample)
                    if piccodeav:
                        if piccodeav.source != 3:
                            return
                        if len(piccodeav.cid) > len(cid):
                            piccodeav.cid = cid
                            piccodeav.piccode = piccode
                            piccodeav.piccount=piccount
                            DBHelper.session.commit()
                            is_update=True

    if not is_update and DBHelper.check_movie_exist_with_title_similar(Tools.get_dvdid(cid,None,3),title):
        return
    if not is_update:
        titleav = DBHelper.check_title_exist_with_studio(title,studio=studio)
        if titleav:
            if titleav.source != 3:
                return
            if len(titleav.cid) > len(cid):
                titleav.cid=cid
                DBHelper.session.commit()
                is_update = True

    code=Tools.get_dvdid(cid,piccode,3)

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
                        piccode=piccode, piccount=piccount, source=3,
                        actresslist=actslist, genrelist=genrelist,histrionlist=histrionlist)

def spider_by_dmm_dvd_maker(makerid):
    pageindex=1
    while True:
        dvdlisturl=f'https://www.dmm.co.jp/mono/dvd/-/list/=/article=maker/id={makerid}/page={pageindex}/'
        html=CrawlerHelper.get_requests(dvdlisturl,cookies=dmmcookie)
        if not html or html.status_code==404:
            return
        if html.url!=dvdlisturl and pageindex>1:
            return
        bs = BeautifulSoup(html.text, "html.parser")
        studio=bs.find('li',class_='active default').get_text()
        print(f'{studio} {str(pageindex)} {dvdlisturl}')
        DBHelper.save_studio_fanzaid(studio,makerid)
        dvdurls=bs.find_all('a',href=re.compile('https://www.dmm.co.jp/mono/dvd/-/detail/=/cid='))
        for dvdurl in dvdurls:
            cid = re.findall('https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=(.*?)/', dvdurl['href'])[0]
            if len(re.findall('^(pb|tk|gk|dk|4k)', cid)) > 0 \
                    or len(re.findall('^[a-z][0-9][a-z]', cid)) > 0 \
                    or len(re.findall('^9[a-z]', cid)) > 0 \
                    or len(re.findall('^(h_|n_)?[0-9]+(pb|tk|gk|dk|4k)', cid)) > 0 \
                    or len(re.findall('[a-z]$', cid)) > 0 \
                    or len(re.findall('tk[0-9]$', cid)) > 0:
                continue
            dvdid=Tools.get_dvdid(cid, None, 3)
            if DBHelper.check_cid_exist(cid) \
                or DBHelper.check_cid_exist(cid.replace(cid.rstrip(string.digits),cid.rstrip(string.digits)+'00',1)) \
                or DBHelper.check_dvdid_exist_with_studioid(dvdid,studio=studio,studio_id=None):
                    continue
            crawler_dmmdvd_page(cid)
        if len(re.findall('次へ',html.text))>0:
            pageindex+=1
        else:
            break
def spider_dmm_dvd_newrelease():
    for pageindex in range(1,30):# maxpage:417
        dvdlisturl = f'https://www.dmm.co.jp/mono/dvd/-/list/=/list_type=release/sort=date/page={pageindex}/'
        html = CrawlerHelper.get_requests(dvdlisturl, cookies=dmmcookie)
        if not html or html.status_code == 404:
            return
        bs = BeautifulSoup(html.text, "html.parser")
        dvdurls = bs.find_all('a', href=re.compile('https://www.dmm.co.jp/mono/dvd/-/detail/=/cid='))
        for dvdurl in dvdurls:
            cid = re.findall('https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=(.*?)/', dvdurl['href'])[0]
            if len(re.findall('^(pb|tk|gk|dk|4k)',cid))>0 \
                    or len(re.findall('^[a-z][0-9]',cid))>0 \
                    or len(re.findall('^9[a-z]', cid)) > 0 \
                    or len(re.findall('^(h_|n_)?[0-9]+(pb|tk|gk|dk|4k)',cid))>0\
                    or len(re.findall('[a-z]$', cid)) > 0 \
                    or len(re.findall('tk[0-9]$', cid)) > 0:
                continue
            dvdid=Tools.get_dvdid(cid, None, 3)
            if DBHelper.check_cid_exist(cid) \
            or DBHelper.check_cid_exist(cid.replace(cid.rstrip(string.digits), cid.rstrip(string.digits) + '00', 1)) \
            or DBHelper.check_dvdid_exist(dvdid):
                continue
            crawler_dmmdvd_page(cid)
if __name__ == '__main__':
    spider_dmm_dvd_newrelease()