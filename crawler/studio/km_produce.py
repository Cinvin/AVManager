import re
import string
import sqlhelper
from crawler import CrawlerHelper, DBHelper
from crawler.shop import fanza_digital,fanza_dvd
from bs4 import BeautifulSoup
from model import AV, Genre

age_cookie={'modal':'off'}#年齢認証 modal=off

def get_studio_from_label(label):
    if label == "Aver VR":
        return "ケイ・エム・プロデュース"
    elif label == "KMP VR":
        return "ケイ・エム・プロデュース"
    elif label == "KMPVR-X-":
        return "ケイ・エム・プロデュース"
    elif label == "S級素人VR":
        return "S級素人"
    elif label == "SCOOP VR":
        return "スクープ"
    elif label == "KMPVR-彩-":
        return "KMPVR-彩-"
    elif label == "BAZOOKA VR":
        return "ケイ・エム・プロデュース"
    elif label == "KMPVR-bibi-":
        return "KMPVR-bibi-"
    elif label == "サロメ・プロローグ":
        return "サロメ"
    elif label == "REAL VR-Neo-":
        return "REAL VR-Neo-"
    elif label == "ステルス":
        return "ステルス"
    elif label == "3D V＆R VR":
        return "V＆R PRODUCE"
    elif label == "KMP Premium":
        return "ケイ・エム・プロデュース"
    elif label.lower() == "million":
        return "ケイ・エム・プロデュース"
    elif label == "millionミント":
        return "ケイ・エム・プロデュース"
    elif label == "REAL":
        return "レアルワークス"
    elif label == "SCOOP":
        return "スクープ"
    elif label == "サロメ":
        return "ケイ・エム・プロデュース"
    elif label == "300":
        return "300 Three Hundred"
    elif label == "俺の素人":
        return "ケイ・エム・プロデュース"
    elif label == "BLACK REAL":
        return "レアルワークス"
    elif label == "おかず。":
        return "ケイ・エム・プロデュース"
    elif label == "UMANAMI":
        return "ケイ・エム・プロデュース"
    elif label == "Nadeshiko":
        return "なでしこ"
    elif label == "100人":
        return "100人-ex-"
    elif label == "GIGOLO":
        return "GIGOLO（ジゴロ）"
    else:
        return label


def get_label_from_label(label):
    if label=="Aver VR":
        return "AverVR"
    elif label=="KMP VR":
        return "KMPVR"
    elif label == "KMPVR-X-":
        return "KMPVR"
    elif label == "S級素人VR":
        return "S級素人VR"
    elif label.lower() == "million":
        return "million（ミリオン）"
    elif label == "millionミント":
        return "million mint（ミリオンミント）"
    elif label == "REAL":
        return "REAL（レアルワークス）"
    elif label == "SCOOP":
        return "SCOOP（スクープ）"
    elif label == "BAZOOKA":
        return "BAZOOKA（バズーカ）"
    elif label == "300":
        return "300 Three Hundred"
    elif label == "俺の素人":
        return "俺の素人（ケイ・エム・プロデュース）"
    elif label == "BLACK REAL":
        return "BLACK REAL（レアルワークス）"
    # elif label == "100人":
    #     return "100人8時間"
    else:
        return label


def spider_avlist():
    baseurl='https://www.km-produce.com/works-sell/page/pageindex'
    pageindex=1
    while True:
        url=baseurl.replace('pageindex', str(pageindex))
        html=CrawlerHelper.get_requests(url,cookies=age_cookie).text
        bs = BeautifulSoup(html, "html.parser")
        ul=bs.find('ul',class_='worklist')
        lis=ul.find_all('li')
        for li in lis:
            link=li.find('a',href=re.compile('/works/(.*?)'))
            dvdid=link['href'].split('/')[-1].upper()
            title=link.get_text()
            labelp=li.find('p',class_='label')
            label=labelp.get_text()
            dds=li.find_all('dd')
            rdate=None
            for dd in dds:
                if '円' not in dd.get_text():
                    rdate=dd.get_text()
                    break
            if not DBHelper.check_dvdid_exist(dvdid):

                if dvdid.startswith('BD'):
                    if DBHelper.check_dvdid_exist(dvdid[2:]):
                        continue
                studio = get_studio_from_label(label)
                label = get_label_from_label(label)

                dvdidprefix = dvdid.rstrip(string.digits)
                avfind = DBHelper.session.query(AV).filter(AV.code.like(f'{dvdidprefix}%')).order_by(
                    AV.rdate.desc()).first()
                if avfind:
                    studio = avfind.studio.name
                    label = avfind.label.name

                print(f'not found:dvdid:{dvdid} label:{label} studio:{studio} rdate:{rdate} title:{title}')
                crawler_detail(dvdid,rdate,studio,label)
            # else:
            #     print(f'existed:dvdid:{dvdid} label:{label} rdate:{rdate} title:{title}')

        next=bs.find('a',class_='next')
        if next:
            pageindex+=1
        else:
            break

def crawler_detail(dvdid,rdate,studio,label):
    url=f'https://www.km-produce.com/works/{dvdid}'
    html = CrawlerHelper.get_requests(url).text
    bs = BeautifulSoup(html, "html.parser")

    cid = dvdid
    piccode = dvdid.lower()
    code = dvdid.upper()

    dmm_digital_cid = None
    dmm_dvd_cid = None
    dmmlink = bs.find('a', href=re.compile('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=(.*?)/'))
    if dmmlink:
        dmm_digital_cid = re.findall('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=(.*?)/', dmmlink['href'])[0]
        if not DBHelper.get_movie_by_cid(1, dmm_digital_cid):
            fanza_digital.crawler_dmmmoive(dmm_digital_cid)
            if sqlhelper.fetchone('select 1 from t_av where cid=%s and source=1', dmm_digital_cid):
                return
    dmmlink=bs.find('a',href=re.compile('http://www.dmm.co.jp/mono/dvd/-/detail/'))
    if dmmlink:
        dmm_dvd_cid = re.findall('http://www.dmm.co.jp/mono/dvd/-/detail/=/cid=(.*?)/', dmmlink['href'])[0]
        if not DBHelper.get_movie_by_cid(3, dmm_dvd_cid):
            fanza_dvd.crawler_dmmdvd_page(dmm_dvd_cid)
            if sqlhelper.fetchone('select 1 from t_av where cid=%s and source=3', dmm_dvd_cid):
                return

    title=bs.find('meta',property='og:title')['content']
    title=title.split('|')[0]

    length=None
    #<dt>収録時間</dt>[\s]*<dd>[\s]*480分[\s]*</dd>
    lenfind=re.findall('<dt>収録時間</dt>[\s]*<dd>[\s]*(\d*)分[\s]*</dd>',html)
    if len(lenfind)>0:
        length=lenfind[0]

    director=None
    #<dt>監督</dt>[\s]*<dd>[\s]*<ul><li>(.*?)</li><ul>[\s]*</dd>
    dirtextarea=re.findall('<dt>監督</dt>[\s]*<dd>[\s]*<ul><li>(.*?)</li><ul>[\s]*</dd>',html)
    if len(dirtextarea)>0:
        dirarea=BeautifulSoup(dirtextarea[0], "html.parser")
        if dirarea:
            dirfind=dirarea.find('a')
            if dirfind:
                director=dirfind.get_text()

    series=None

    piccount=0
    picturearea=bs.find('div',class_='sample')
    if picturearea:
        piclist=picturearea.find_all('img')
        for pic in piclist:
            if 'still' in pic['src']:
                piccount+=1
    actslist = []
    areaact = bs.find('dd', class_='act')
    if areaact:
        actas = areaact.find_all('a')
        for acta in actas:
            actslist.append(acta.get_text())

    genrelist=[]
    # <dt>ジャンル</dt>[\s]*<dd><ul><li>(.*?)</li>
    genretextarea=re.findall('<dt>ジャンル</dt>[\s]*<dd>(.*?)</dd>',html)
    if len(genretextarea)>0:
        genrebs = BeautifulSoup(genretextarea[0], "html.parser")
        if genrebs:
            genresfind = genrebs.find_all('a')
            for genrefind in genresfind:
                genre=genrefind.get_text()
                if not DBHelper.session.query(Genre).filter_by(name_ja=genre).first():
                    continue
                genrelist.append(genrefind.get_text())

    source = 1004
    if dmm_digital_cid:
        picpl = CrawlerHelper.get_requests(
            f'https://pics.dmm.co.jp/digital/video/{dmm_digital_cid}/{dmm_digital_cid}pl.jpg', is_stream=True)
        picplexist = "now_printing" not in picpl.url
        if picplexist:
            source = 1
            cid = dmm_digital_cid
            piccode = dmm_digital_cid
    if dmm_dvd_cid and source != 1:
        picpl = CrawlerHelper.get_requests(
            f'https://pics.dmm.co.jp/mono/movie/adult/{dmm_dvd_cid}/{dmm_dvd_cid}pl.jpg', is_stream=True)
        picplexist = "now_printing" not in picpl.url
        if picplexist:
            source = 3
            cid = dmm_dvd_cid
            piccode = dmm_dvd_cid
            piccount=0

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
    DBHelper.save_movie(code=code, cid=cid, title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=piccount, source=source,
                        actresslist=actslist, genrelist=genrelist)

if __name__ == '__main__':
    spider_avlist()
    # crawler_detail('UMSO-382','2021/3/12','ケイ・エム・プロデュース','UMANAMI')
    # crawler_detail('BDSAMA-025','2012/12/14','S級素人','S級素人')
    # crawler_detail('vrkm-252','2021/6/17','ケイ・エム・プロデュース','KMP VR')