import re
import string

from bs4 import BeautifulSoup
import sys
sys.path.append("..")
from crawler import DBHelper,CrawlerHelper,Tools
from crawler.shop import fanza_digital,fanza_dvd
import sqlhelper

def spider_avlist_by_date():
    listurl=f'https://www.madonna-av.com/works/date/'
    html=CrawlerHelper.get_requests(listurl).text
    bs = BeautifulSoup(html, "html.parser")
    links = bs.find_all('a', href=re.compile('/works/list/date/(.*?)/'))
    for link in links:
        movielisturl=link['href']
        rdate=re.findall('/works/list/date/(.*?)/',movielisturl)[0]
        # if rdate[0:4]>='2007':
        #     continue
        rdate=rdate[0:4]+'-'+rdate[4:6]+'-'+rdate[6:]
        print(f'rdate:{rdate}')
        #https://www.madonna-av.com/works/list/date/20020301/
        htmlml=CrawlerHelper.get_requests('https://www.madonna-av.com'+movielisturl).text
        bsml = BeautifulSoup(htmlml, "html.parser")
        movielinks = bsml.find_all('a', class_='works-list-item-img',href=re.compile('/works/detail/(.*?)/'))
        for ml in movielinks:
            movieurl=ml['href']
            urlid = re.findall('/works/detail/(.*?)/', movieurl)[0]
            dvdid2=urlid.upper()
            dvdidprefix=dvdid2.rstrip(string.digits)
            dvdid2=dvdid2.replace(dvdidprefix,dvdidprefix+'-')

            av=DBHelper.check_dvdid_exist_with_studioid(dvdid2, studio='マドンナ')
            if not av:
                av = DBHelper.check_dvdid_exist_with_studioid(dvdid2, studio='Fitch')
            if av:
                av.rdate=rdate
                DBHelper.session.commit()
                print(f'db exists {dvdid2} {rdate}')
                continue
            else:
                print(f'db not found {dvdid2} {rdate}')
                #crawler_detail(urlid, rdate)

def crawler_detail(urlid,rdate):
    url=f'https://www.madonna-av.com/works/detail/{urlid}/'
    html = CrawlerHelper.get_requests(url).text
    bs = BeautifulSoup(html, "html.parser")

    cid = urlid
    piccode = urlid
    code = urlid.upper()
    codeprefix = code.rstrip(string.digits)
    code = code.replace(codeprefix, codeprefix + '-')
    if code.startswith('MI') and code[3] == '-':
        code = code[0:3] + 'D' + code[3:]
    elif code.startswith('MD') and code[3] == '-':
        code = code[0:3] + 'D' + code[3:]
    elif code.startswith('RI') and code[3] == '-':
        code = code[0:3] + 'D' + code[3:]

    dmmlinks=bs.find_all('a',class_='m-primary-btn')
    dmm_digital_cid=None
    dmm_dvd_cid=None
    for dmmlink in dmmlinks:
        dmmurl=dmmlink['href']
        #http://www.dmm.co.jp/digital/videoa/-/detail/=/cid=
        if dmmurl.startswith('http://www.dmm.co.jp/digital/videoa/-/detail/=/cid='):
            dmm_digital_cid=re.findall('http://www.dmm.co.jp/digital/videoa/-/detail/=/cid=(.*?)/',dmmurl)[0]
            if not DBHelper.get_movie_by_cid(1, dmm_digital_cid):
                fanza_digital.crawler_dmmmoive(dmm_digital_cid)
                if sqlhelper.fetchone('select 1 from t_av where cid=%s and source=1',dmm_digital_cid):
                    return
            code = Tools.get_dvdid(dmm_digital_cid, dmm_digital_cid, 1)
            if DBHelper.check_dvdid_exist_with_studioid(code, studio='マドンナ'):
                return
        elif dmmurl.startswith('http://www.dmm.co.jp/mono/dvd/-/detail/=/cid='):
            dmm_dvd_cid=re.findall('http://www.dmm.co.jp/mono/dvd/-/detail/=/cid=(.*?)/',dmmurl)[0]
            if not DBHelper.get_movie_by_cid(3, dmm_dvd_cid):
                fanza_dvd.crawler_dmmdvd_page(dmm_dvd_cid)
                if sqlhelper.fetchone('select 1 from t_av where cid=%s and source=3',dmm_dvd_cid):
                    return
            code=Tools.get_dvdid(dmm_dvd_cid,dmm_digital_cid,3)
            if DBHelper.check_dvdid_exist_with_studioid(code, studio='マドンナ'):
                return
    title=bs.find('meta',property='og:title')['content']

    length=None
    lenfind=re.findall('DVD</span>(\d*)分',html)
    if len(lenfind)>0:
        length=lenfind[0]
    else:
        lenfind = re.findall('動画</span>(\d*)分', html)
        if len(lenfind) > 0:
            length = lenfind[0]

    director=None
    dirfind=bs.find('a',href=re.compile('/works/list/director/(\d*)/'))
    if dirfind:
        director=dirfind.get_text()

    studio='マドンナ'
    label=None
    labelfind = bs.find('a', href=re.compile('/works/list/label/(\d*)/'))
    if labelfind:
        label = labelfind.get_text()
        if sqlhelper.fetchone('select 1 from t_label where name=%s','MOODYZ '+label):
            label='MOODYZ '+label
    series=None
    seriesfind = bs.find('a', href=re.compile('/works/list/series/(\d*)/'))
    if seriesfind:
        series = seriesfind.get_text()

    piccount=0
    picturearea=bs.find('div',id='js-sample-image')
    if picturearea:
        piccount=len(picturearea.find_all('img'))
    actslist = []
    areaact = bs.find('ul', class_='works-detail-info--actress')
    if areaact:
        actas = areaact.find_all('a', href=re.compile('/actress/detail/(\d*)/'))
        for acta in actas:
            actslist.append(acta.get_text())
        actps = areaact.find_all('p')
        for actp in actps:
            actslist.append(actp.get_text())
    genrelist=[]
    genrefind = bs.find_all('a', href=re.compile('/works/list/genre/(\d*)/'))
    for genretag in genrefind:
        genrelist.append(genretag.get_text())

    source='??????'
    if dmm_digital_cid:
        picpl=CrawlerHelper.get_requests(f'https://pics.dmm.co.jp/digital/video/{dmm_digital_cid}/{dmm_digital_cid}pl.jpg',is_stream=True)
        picplexist="now_printing" not in picpl.url
        if picplexist:
            source=1
            cid=dmm_digital_cid
            piccode = dmm_digital_cid
    if dmm_dvd_cid and source != 1:
        picpl = CrawlerHelper.get_requests(
            f'https://pics.dmm.co.jp/mono/movie/adult/{dmm_dvd_cid}/{dmm_dvd_cid}pl.jpg',is_stream=True)
        picplexist = "now_printing" not in picpl.url
        if picplexist:
            source = 3
            cid = dmm_dvd_cid
            piccode = dmm_dvd_cid
    if source != 1004:
        piccount = 0
    print(f"dmm_digital_cid:{dmm_digital_cid}")
    print(f"dmm_dvd_cid:{dmm_dvd_cid}")
    print(f"cid:{cid}")
    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    print(f'director:{director}')
    print(f'studio:{studio}')
    print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount} source:{source}')
    print(actslist)
    print(genrelist)
    # DBHelper.save_movie(code=code, cid=cid, title=title, length=length, rdate=rdate,
    #                     director=director, studio=studio, label=label, series=series,
    #                     piccode=piccode, piccount=piccount, source=source,
    #                     actresslist=actslist, genrelist=genrelist)
if __name__=='__main__':
    spider_avlist_by_date()
    #crawler_detail('miv005','2006-09-01')
