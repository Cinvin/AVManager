from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper
from datetime import datetime
import sqlhelper
from crawler import DBHelper

# setting
freq = 1 # second
javlibraryurl = 'http://www.d52q.com/ja'

def spider_javlibrary_movie_page(url):
    html = CrawlerHelper.get_requests(url)
    if html is None:
        html = CrawlerHelper.get_requests(url)
    if html is None:
        return
    if html.status_code != 200:
        raise Exception(f'{html.status_code} 请检查 {url}')

    html = html.text
    if len(html) == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 内容为空{url}")
        return
    bs = BeautifulSoup(html, "html.parser")

    pic = bs.find('img',src=re.compile('//pics.dmm.co.jp/mono/movie/adult/(.*?)pl.jpg'))
    if pic:
        cid=re.findall('//pics.dmm.co.jp/mono/movie/adult/(.*?)/',pic['src'])[0]
        piccode=cid
    else:
        return
    titletext=bs.title.get_text().replace(' - JAVLibrary','',1)
    code=titletext.split(' ',maxsplit=1)[0]
    title = titletext.split(' ', maxsplit=1)[1]
    #
    length = re.findall('<td class="header">収録時間:</td>[\s]*<td><span class="text">(\d*)</span> 分</td>',
                        html)
    if len(length) > 0:
        length = length[0]
    else:
        length = None
    #発売日:</td>[\s]*<td class="text">2001-05-23</td>
    rdate = re.findall('発売日:</td>[\s]*<td class="text">(.*?)</td>',
                        html)
    if len(rdate) > 0:
        rdate = rdate[0]
    else:
        rdate = None
    director = bs.find('a',href=re.compile('vl_director.php\?'))
    if director:
        director = director.get_text()
    makerspan=bs.find('span', class_='maker')
    studio=None
    if makerspan:
        tagmaker = makerspan.find('a')
        studio = tagmaker.get_text()
        makercode = tagmaker['href'].split('=',maxsplit=1)[1]
        if not sqlhelper.fetchone('select 1 from javlibrary_maker where studio_code=%s',makercode):
            sqlhelper.execute('insert into javlibrary_maker(studio_code,studio_name) values(%s,%s)',makercode,studio)
    labelspan = bs.find('span', class_='label')
    label=None
    if labelspan:
        label = labelspan.find('a').get_text()

    series=None

    genrelist=[]
    divgenre=bs.find('div',id='video_genres')
    if divgenre:
        genres=divgenre.find_all('a',href=re.compile('vl_genre.php\?'))
        for genre in genres:
            g=genre_transfrom(genre.get_text())
            genrelist.append(g)
    actresslist = []
    divactress = bs.find('div',id='video_cast')
    if divactress:
        actresses = divactress.find_all('a', href=re.compile('vl_star.php\?'))
        for actress in actresses:
            actresslist.append(actress.get_text())

    piccount=0
    divpreviewthumbs=bs.find('div',class_='previewthumbs')
    if divpreviewthumbs:
        pics=divpreviewthumbs.find_all('img',src=re.compile('pics.dmm.co.jp/digital/video/'))
        piccount=len(pics)
        if piccount:
            piccode = piccode + ' '+re.findall('pics.dmm.co.jp/digital/video/(.*?)/',pics[0]['src'])[0]
    # 保存
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
    print(actresslist)
    #print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code, cid=cid, title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=piccount, source=3,
                        actresslist=actresslist, genrelist=genrelist)

def spider_by_maker():
    result=sqlhelper.fetchall('select studio_code from javlibrary_maker where flag=0')
    for item in result:
        makercode=item['studio_code']
        spider_maker_list(makercode)
        sqlhelper.execute('update javlibrary_maker set flag=1 where studio_code=%s',makercode)

def spider_maker_list(makercode,pageindex = 1):
    #http://www.k51r.com/ja/vl_maker.php?m=le
    #http://www.k51r.com/ja/vl_maker.php?&mode=2&m={makercode}&page={pageindex}
    while True:
        makerlisturl = f'{javlibraryurl}/vl_maker.php?&mode=2&m={makercode}&page={pageindex}'
        html=CrawlerHelper.get_requests(makerlisturl).text
        bs = BeautifulSoup(html, "html.parser")
        studio=bs.find('div',class_='boxtitle').get_text().replace('のビデオ','')
        print(f'{studio} {pageindex}')
        divvideothumblist=bs.find('div',class_='videothumblist')
        videos=divvideothumblist.find_all('div',class_='video')
        for video in videos:
            link=video.find('a')
            url = javlibraryurl+link['href'].lstrip('.')
            code = link['title'].split(' ',maxsplit=1)[0]
            title = link['title'].split(' ', maxsplit=1)[1]
            if not DBHelper.check_dvdid_exist_with_studioid(code=code,studio=studio) and not DBHelper.check_movie_exist_with_title_similar(code,title=title):
                spider_javlibrary_movie_page(url)

        #次のページ
        if len(re.findall('次のページ',html))>0:
            pageindex+=1
        else:
            break

def spider_by_genre():
    #http://www.k51r.com/ja/vl_maker.php?m=le
    #http://www.k51r.com/ja/vl_maker.php?&mode=2&m={makercode}&page={pageindex}
    genrelisturl=f'{javlibraryurl}/genres.php'
    html=CrawlerHelper.get_requests(genrelisturl).text
    bs = BeautifulSoup(html, "html.parser")
    genrelist=[]
    genretag=bs.find_all('div',class_='genreitem')
    for genre in genretag:
        genrelist.append(genre.a['href'].split('=',maxsplit=1)[1])
    genrelist.sort()
    for genre in genrelist:
        if genre<'oq':
            continue
        pageindex=1
        while True:
            makerlisturl = f'{javlibraryurl}/vl_genre.php?&mode=2&g={genre}&page={pageindex}'
            html=CrawlerHelper.get_requests(makerlisturl).text
            bs = BeautifulSoup(html, "html.parser")
            genretext=bs.find('div',class_='boxtitle').get_text().replace('関連のビデオ','')
            print(f'{genretext} {pageindex} {makerlisturl}')
            divvideothumblist=bs.find('div',class_='videothumblist')
            videos=divvideothumblist.find_all('div',class_='video')
            for video in videos:
                link=video.find('a')
                url = javlibraryurl+link['href'].lstrip('.')
                code = link['title'].split(' ',maxsplit=1)[0]
                title = link['title'].split(' ', maxsplit=1)[1]
                if not DBHelper.check_movie_exist_with_title_similar(code,title=title):
                    spider_javlibrary_movie_page(url)

            #次のページ
            if len(re.findall('次のページ',html))>0:
                pageindex+=1
            else:
                break

def crawler_newentries():
    #http://www.k51r.com/ja/vl_newentries.php?&mode=&page=9
    pageindex=1
    while True:
        makerlisturl = f'{javlibraryurl}/vl_newentries.php?&mode=&page={pageindex}'
        html=CrawlerHelper.get_requests(makerlisturl).text
        bs = BeautifulSoup(html, "html.parser")
        divvideothumblist=bs.find('div',class_='videothumblist')
        videos=divvideothumblist.find_all('div',class_='video')
        for video in videos:
            link=video.find('a')
            url = javlibraryurl+link['href'].lstrip('.')
            code = link['title'].split(' ',maxsplit=1)[0]
            title = link['title'].split(' ', maxsplit=1)[1]
            imgsrc=video.find('img')['src']
            if not imgsrc.startswith('//pics.dmm.co.jp/mono/movie/adult/'):
                continue
            cid=re.findall('//pics.dmm.co.jp/mono/movie/adult/(.*?)/',imgsrc)
            if len(cid) == 0:
                continue
            cid = cid[0]

            if not DBHelper.check_cid_exist(cid) and \
                    not DBHelper.check_movie_exist_with_title_similar(code, title=title):
                spider_javlibrary_movie_page(url)

        #次のページ
        if len(re.findall('次のページ',html))>0:
            pageindex+=1
        else:
            break

def genre_transfrom(genre):
    if genre=='芸能人':
        return 'アイドル・芸能人'
    elif genre=='縛り':
        return '縛り・緊縛'
    return genre

if __name__ == '__main__':
    #crawler_newentries()
    spider_javlibrary_movie_page('https://d52q.com/ja/?v=javli6by6u')