from bs4 import BeautifulSoup
import re

import sqlhelper
from crawler import CrawlerHelper
from time import sleep
from crawler import DBHelper
#https://www.japorn.tv/
# setting
freq = 0.5 # second
def spider_studio_list():
    url='https://www.aventertainments.com/studiolists.aspx?languageID=2'
    html = CrawlerHelper.get_requests(url).text
    bs = BeautifulSoup(html, "html.parser")
    atags=bs.find_all('a',href=re.compile('StudioID'))
    nowstdio=None
    atags = set(atags)
    atags = sorted(atags, key=lambda x: x.get_text())
    for a in atags:
        studio=a.get_text()
        if nowstdio:
            if nowstdio not in studio:
                continue
            else:
                nowstdio=None
        print(f'studio:{studio}')
        spider_movielist(a['href'])

def spider_movielist(urlbase):
    urlbase=urlbase+'&Rows=3&SaveData=3&CountPage='
    pageindex=1
    while True:
        html = CrawlerHelper.get_requests(urlbase+str(pageindex)).text
        bs = BeautifulSoup(html, "html.parser")
        videos = bs.find_all('div', class_='single-slider-product__content')
        for video in videos:
            code=video.find('small').get_text()
            code=code.replace('商品番号: ', '')
            vedioa=video.find('a',href=re.compile('product_lists.aspx\?product_id='))
            title = vedioa.get_text()
            if DBHelper.check_movie_exist_with_title_similar(code,title):
                continue
            if code.startswith('HEY-'):
                continue
            link=vedioa['href']
            print(f'{code} {title} {link}')
            crawler_moviepage_dvd(link)
            sleep(freq)
        next=bs.find('a',href=re.compile('CountPage='+str(pageindex+1)))
        if next:
            pageindex+=1
        else:
            break

def spider_new_dvdlist():
    spider_movielist('https://www.aventertainments.com/subdept_products.aspx?Dept_ID=29&SubDept_ID=45&languageID=2')

def crawler_moviepage_dvd(url):
    res = CrawlerHelper.get_requests(url)
    if not res or res.status_code == 404:
        print('404!')
        return
    html = res.text
    if len(re.findall('404 PAGE NOT FOUND',html))>0:
        print('404!')
        return
    bs = BeautifulSoup(html, "html.parser")
    title = bs.find('h3').get_text()
    infodiv = bs.find('div', class_='product-info-block-rev')

    code=bs.find('span',class_='tag-title').get_text()

    rdate = None
    rdatere = re.findall('発売日</span>[\s]*<span class="value">(.*?) <span', html)
    if len(rdatere) > 0:
        rdate = rdatere[0]
        rdates = rdate.split('/')
        rdate = f'{rdates[2]}-{rdates[0]}-{rdates[1]}'

    length = None
    lengthre = re.findall('収録時間</span>[\s]*<span class="value">apx.[\s]*(.*?)[\s]*min', html.lower())
    if len(lengthre) > 0 and len(lengthre[0]):
        length = lengthre[0].strip()
        if length=='hr':
            length=None
        elif 'hr' in length:
            lengthsp = length.split(' ')
            length = int(lengthsp[0]) * 60 + int(lengthsp[-1])
        elif '+' in length:
            lengthsp = length.split('+')
            length=0
            for l in lengthsp:
                length=length+int(l)
    product_id = re.findall('product_id=(.*?)&',url)[0]
    tab_area = bs.find('div',class_='tab-area')
    atags = tab_area.find_all('a')
    a_self = tab_area.find('a', href=re.compile('product_id='+product_id))
    if a_self:
        a_self=a_self.get_text()
        if a_self == 'DVD':
            for atag in atags:
                if 'PPV' in atag.get_text():
                    crawler_moviepage_ppv(atag['href'],code,rdate,length)
                    return
        elif a_self == 'Blu-ray':
            for atag in atags:
                if 'PPV HD' in atag.get_text():
                    crawler_moviepage_ppv(atag['href'],code,rdate,length)
                    return
        elif a_self == 'Blu-ray 3D':
            for atag in atags:
                if '3D PPV HD' in atag.get_text():
                    crawler_moviepage_ppv(atag['href'],code,rdate,length)
                    return

    rdate=None
    rdatere=re.findall('発売日</span>[\s]*<span class="value">(.*?) <span',html)
    if len(rdatere)>0:
        rdate=rdatere[0]
        rdates=rdate.split('/')
        rdate=f'{rdates[2]}-{rdates[0]}-{rdates[1]}'


    studio=infodiv.find('a', href=re.compile('/studio_'))
    if studio:
        studio=studio.get_text()
    series = infodiv.find('a', href=re.compile('Series.aspx'))
    if series:
        series = series.get_text()
    actressfounds = infodiv.find_all('a', href=re.compile('Actress'))
    actresslist= [a.get_text().strip() for a in actressfounds]

    genrefounds = infodiv.find_all('a', href=re.compile('subdept'))
    genrelist = [a.get_text().strip() for a in genrefounds if '$' not in a.get_text()]
    if '完全無修正' in genrelist:
        genrelist.remove('完全無修正')
    if 'サンプル動画上映中' in genrelist:
        genrelist.remove('サンプル動画上映中')
    if '最新入荷済み商品' in genrelist:
        genrelist.remove('最新入荷済み商品')

    piccode=re.findall('jacket_images/(.*?).jpg',bs.find('link',rel='image_src')['href'])[0]
    source=6
    piccount = 0
    divgallery = bs.find('div', class_='grid-gallery')
    if divgallery:
        imgs = divgallery.find_all('img')
        piccount = len(imgs)
        if piccount>0:
            piccodedt = re.findall('/large/(.*?)/', imgs[0]['src'])
            if len(piccodedt):
                if piccode != piccodedt[0]:
                    piccode = piccode + ' ' + piccodedt[0]

    video = bs.find('video', id='player1')
    if video:
        url = video.find('source')['src']
        video = url.replace('https://ppvclips02.aventertainments.com/', '')
        piccode += '|' + video

    #print(f"cid:{cid}")
    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    #print(f'director:{director}')
    print(f'studio:{studio}')
    #print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount}')
    print(actresslist)
    # print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code, category=2, cid=None, title=title, length=length, rdate=rdate,
                        director=None, studio=studio, label=None, series=series,
                        piccode=piccode, piccount=piccount, source=5,
                        actresslist=actresslist, genrelist=genrelist)

def spider_studio_list_ppv():
    url='https://www.aventertainments.com/ppv/ppv_studiolists.aspx?languageID=2&VODTypeID=1'
    html = CrawlerHelper.get_requests(url).text
    bs = BeautifulSoup(html, "html.parser")
    atags=bs.find_all('a',href=re.compile('StudioID'))
    exclude=['カリビアンコム','一本道','HEYZO','天然むすめ','パコパコママ']
    nowstdio='J-Fantasy'
    atags = set(atags)
    atags = sorted(atags, key=lambda x: x.get_text())
    for a in atags:
        studio=a.get_text().split('(',1)[0].strip()
        if studio in exclude:
            continue
        if nowstdio:
            if nowstdio not in studio:
                continue
            else:
                nowstdio=None
        print(f'studio:{studio}')
        spider_movielist_ppv(a['href'])

def spider_movielist_ppv(urlbase):
    urlbase=urlbase+'&Rows=3&SaveData=3&CountPage='
    pageindex=1
    while True:
        html = CrawlerHelper.get_requests(urlbase+str(pageindex)).text
        bs = BeautifulSoup(html, "html.parser")
        videos = bs.find_all('div', class_='single-slider-product__content')
        for video in videos:
            code=video.find('small').get_text()
            code=code.replace('商品番号: ', '')
            vedioa=video.find('a',href=re.compile('new_detail.aspx\?ProID='))
            title = vedioa.get_text()
            title = re.sub('\([\s]*HD\)[\s]*', '', title)
            title = re.sub('\([\s]*FULL[\s]*HD\)[\s]*', '', title)
            title = re.sub('\([\s]*Full[\s]*HD\)[\s]*', '', title).strip()
            if DBHelper.check_movie_exist_with_title_similar(code,title):
                continue
            link=vedioa['href']
            if code.startswith('DL'):
                code = code.replace('DL', '', 1)
            elif code.startswith('dl'):
                code = code.replace('dl', '', 1)
            if code.endswith('HD'):
                code = code[:-2]
            elif code.endswith('-1'):
                code = code[:-2]
            if '_' in code:
                code=code.split('_',1)[1]
            if DBHelper.check_movie_exist_with_title_similar(code,title):
                continue
            if code.startswith('HEY-'):
                continue
            if len(re.findall('20\d\d\d\d\d',code)) > 0:
                continue
            print(f'{code} {title} {link}')
            crawler_moviepage_ppv(link)
            sleep(freq)
        next=bs.find('a',href=re.compile('CountPage='+str(pageindex+1)))
        if next:
            pageindex+=1
        else:
            break

def spider_new_ppvlist():
    spider_movielist_ppv('https://www.aventertainments.com/ppv/dept.aspx?cat_id=229&languageID=2&vodtypeid=1')

def crawler_moviepage_ppv(url,code=None,rdate=None,length=None):
    res = CrawlerHelper.get_requests(url)
    if not res or res.status_code==404:
        print('404!')
        return
    html=res.text
    if len(re.findall('404 PAGE NOT FOUND',html))>0:
        print('404!')
        return
    bs = BeautifulSoup(html, "html.parser")
    title = bs.find('h3').get_text()
    title = re.sub('\([\s]*HD\)[\s]*', '', title)
    title = re.sub('\([\s]*FULL[\s]*HD\)[\s]*', '', title)
    title = re.sub('\([\s]*Full[\s]*HD\)[\s]*', '', title).strip()
    infodiv = bs.find('div', class_='product-info-block-rev')
    if not code:
        tab_area = bs.find('div', class_='tab-area')
        if tab_area:
            atags = tab_area.find_all('a')
            for atag in atags:
                if 'DVD' in atag.get_text() or 'blu-ray' in atag.get_text().lower():
                    return
        code=infodiv.find('span',class_='tag-title').get_text()

    if code.startswith('DL'):
        code = code.replace('DL', '',1)
    if code.startswith('dl'):
        code = code.replace('dl', '',1)
    if code.endswith('HD'):
        code = code[:-2]
    elif code.endswith('-1'):
        code = code[:-2]
    if '_' in code:
        code = code.split('_', 1)[1]
    if not rdate:
        rdatere=re.findall('発売日</span>[\s]*<span class="value">(.*?) <span',html)
        if len(rdatere)>0:
            rdate=rdatere[0]
            rdates=rdate.split('/')
            rdate=f'{rdates[2]}-{rdates[0]}-{rdates[1]}'

    if not length:
        lengthre = re.findall('収録時間</span>[\s]*<span class="value">(.*?)</span>', html)
        if len(lengthre) > 0:
            lengthsplits = lengthre[0].split(':')
            if len(lengthsplits)>1:
                length = int(lengthsplits[0]) * 60 + int(lengthsplits[1])
            else:
                length = None

    exclude = ['カリビアンコム', '一本道', 'HEYZO', '天然むすめ', 'パコパコママ']
    studio=infodiv.find('a', href=re.compile('ppv_studioproducts'))
    if studio:
        studio=studio.get_text()
        if studio in exclude:
            return
    series = infodiv.find('a', href=re.compile('ppv_seriesproducts'))
    if series:
        series = series.get_text()
    actressfounds = infodiv.find_all('a', href=re.compile('Actress'))
    actresslist= [a.get_text().strip() for a in actressfounds]

    genrefounds = infodiv.find_all('a', href=re.compile('Cat_ID'))
    genrelist = [a.get_text().strip() for a in genrefounds if '$' not in a.get_text()]
    genreremove=['完全無修正','フルHDムービー','HD高画質ムービー','ストリーミング配信','サンプル動画上映中','最新入荷済み商品','iPhone/iPad対応']
    for genre in genreremove:
        if genre in genrelist:
            genrelist.remove(genre)

    piccode=re.findall('xlarge/(.*?).jpg',bs.find('div',id='PlayerCover').find('img')['src'])[0]
    source=5
    piccount = 0
    divgallery = bs.find('div', id='sscontainerppv123')
    if divgallery:
        imgs = divgallery.find_all('img')
        piccount = len(imgs)
        if piccount>0:
            piccodedt = re.findall('/large/(.*?)/', imgs[0]['src'])
            if len(piccodedt):
                if piccode != piccodedt[0]:
                    piccode = piccode + ' ' + piccodedt[0]
    video=bs.find('video',id='player1')
    if video:
        url=video.find('source')['src']
        video=url.replace('https://ppvclips02.aventertainments.com/','')
        piccode+='|'+video

    #print(f"cid:{cid}")
    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    #print(f'director:{director}')
    print(f'studio:{studio}')
    #print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount}')
    print(actresslist)
    # print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code, category=2, cid=None, title=title, length=length, rdate=rdate,
                        director=None, studio=studio, label=None, series=series,
                        piccode=piccode, piccount=piccount, source=6,
                        actresslist=actresslist, genrelist=genrelist)

def get_avatars():
    keywordlist = ['1', '6', '11', '16', '21', '26', '31', '36', '39', '44']
    for i in range(1, 11):
        url = f'https://www.aventertainments.com/Artresslistsjp.aspx?languageID=2&Head_id={keywordlist[i - 1]}&g={i}'
        html = CrawlerHelper.get_requests(url).text
        bs = BeautifulSoup(html, "html.parser")
        imgs = bs.find_all('img', src=re.compile('https://imgs02.aventertainments.com/ActressImage/LargeImage/.*?.jpg'),
                           class_='img-fluid')
        for img in imgs:
            actname = img['title']
            url = img['src']
            res = sqlhelper.fetchone(
                'select id from t_actress a where avatar is null and actname=%s and exists(select 1 from t_av_actress b where a.id=b.actress_id and exists(select 1 from t_av c where c.id=b.av_id and c.source in (5,6)))',
                actname)
            if res:
                sqlhelper.execute('update t_actress set avatar=%s where id=%s', url, res['id'])
                print(actname, url, res['id'])

if __name__ == '__main__':
    #spider_new_dvdlist()
    #spider_studio_list_ppv()
    spider_studio_list()
