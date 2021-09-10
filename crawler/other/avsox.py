from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper
from datetime import datetime
from time import sleep
from crawler import DBHelper
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

# setting
freq = 1 # second
avmoourl = 'avmoo.casa'

def spider_avsox_movie_page(url, small_poster_code, studio):
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

    # 番号+标题
    title = re.findall("<h3>(.*?)</h3>", html)
    # 番号
    code = re.findall(('<p><span class="header">品番:</span> <span style="color:#CC0000;">(.*?)</span></p>'), html)
    code = code[0]

    # 标题
    title = title[0]
    title = str(title).replace(code, "").strip()

    # 发行时间

    findrdate = re.findall('<p><span class="header">発売日:</span> (.*?)</p>', html)
    rdate = None
    if len(findrdate) and len(findrdate[0]) > 0:
        rdate = findrdate[0]

    findlength = re.findall('<p><span class="header">収録時間:</span> (\d*)分</p>', html)
    length = None
    if len(findlength) > 0:
        length = findlength[0]

    director = bs.find_all('a', href=re.compile("director"))
    if len(director) > 0:
        director = director[0].get_text()
    else:
        director = None
    # studio = bs.find_all('a', href=re.compile("studio"))
    # if len(studio) > 0:
    #     studio = studio[0].get_text()
    # else:
    #     studio = None
    label = bs.find_all('a', href=re.compile("label"))
    if len(label) > 0:
        label = label[0].get_text()
    else:
        label = None
    series = bs.find_all('a', href=re.compile("series"))
    if len(series) > 0:
        series = series[0].get_text()
    else:
        series = None

    # 演员
    acttags = bs.find_all('a', href=re.compile("star"))
    actresslist = []
    for acttag in acttags:
        act = re.findall('<span>(.*?)</span>', str(acttag.contents))
        if len(act) > 0:
            actname = str(act[0])
            actresslist.append(actname)

    large_poster_code = re.findall("us.netcdn.space/storage/(.*?)$", bs.find('a',class_='bigImage')['href'])[0]
    piccode=f'{small_poster_code} {large_poster_code}'
    # 番号的类型
    genretags = bs.find_all('span', class_="genre")
    genrelist = []
    for tag in genretags:
        genre = tag.get_text()
        if len(genre) > 0:
            genrelist.append(genre)

    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    print(f'director:{director}')
    print(f'studio:{studio}')
    print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode}')
    print(actresslist)
    # print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code, category=2, cid=None, title=title, length=length, rdate=rdate,
                        director=None, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=0,source=7,
                        actresslist=actresslist, genrelist=genrelist)

def crawler_studio_movielist_page(pageurl, second):
    pageindex = 1
    # 页面循环
    while 1 == 1:
        print(f"crawler_movielist_page 爬第{pageindex}页")
        html = CrawlerHelper.get_requests(f"{pageurl}/page/{pageindex}").text
        bs = BeautifulSoup(html, "html.parser")
        studio=bs.title.get_text().replace(' - メーカー - 映画 - AVSOX','',1)
        #print(studio)
        boxlist = bs.find_all("a", class_="movie-box")
        for box in boxlist:
            url = box["href"]
            code = box.find_all("date")[0].get_text()

            src = box.find_all("img")[0]["src"]
            small_poster_code = re.findall("us.netcdn.space/storage/(.*?)$", src)
            if len(small_poster_code)==0:
                continue
            small_poster_code=small_poster_code[0]
            if not small_poster_code.startswith('ave/'):
                print(f'found:{studio} {small_poster_code} {url}')
            return
            # if not DBHelper.check_dvdid_exist_with_studioid(code,studio):
            #     spider_avsox_movie_page('https:'+url, small_poster_code, studio)
        # 本页爬完 到下一页
        findnext = re.findall("次へ ", html)
        if len(findnext) > 0:
            pageindex = pageindex + 1
            sleep(second)
        else:
            break

def spider_avsox_by_studio(second):
    link = f"https://avsox.website/ja/sitemap-studio-(index).xml"
    index = 1
    while True:
        html = CrawlerHelper.get_requests(link.replace('(index)', str(index)))
        if html.status_code != 200:
            raise Exception(f'{html.status_code} {link} 请检查')

        html = html.text

        bs = BeautifulSoup(html, "xml")

        links = bs.find_all("loc")
        if len(links) == 0:
            break
        for i in range(0, len(links)):
            linktag = links[i]
            movielink = linktag.get_text()
            print(f"spider_avsox_by_studio 爬 第{index}页的{i}个 url: {movielink}")
            crawler_studio_movielist_page('https:'+movielink, second)
            sleep(second)
        index += 1
if __name__ == '__main__':
    crawler_studio_movielist_page('https://avsox.website/cn/studio/74a9d0e356f0b5b8',freq)
    #crawler_studio_movielist_page('https://avsox.website/ja/studio/fdf3210612fe509d',freq)# Gachinco
    #crawler_studio_movielist_page('https://avsox.website/ja/studio/b6dd7905ec0d7da4',freq)# 100 girls
    #crawler_studio_movielist_page('https://avsox.website/ja/studio/652307388d7eb203',freq)# 1000人斬り
    #女体のしんぴ nyoshin/contents/1973/thum1.jpg //avsox.website/ja/movie/74f5e70959296f84
    #レズのしんぴ lesshin/contents/1221/thum1.jpg //avsox.website/ja/movie/cf251bc5191be00d
    #うんこたれ unkotare/moviepages/ori10407/images/list.jpg //avsox.website/ja/movie/edbf73ad02dd8f22
    #本生素人TV honnamatv/images/flash384x216/145130.jpg //avsox.website/ja/movie/0dad8a8b89372ff7
    #av9898/images/flash384x216/144620.jpg //avsox.website/ja/movie/f874edc87544b6e3
    #Hey動画 heydouga/images/flash384x216/150400.jpg //avsox.website/ja/movie/75b08cb8d1035f1e
    #人妻斬り c0930/moviepages/hitozuma1306/images/thumb_s.jpg //avsox.website/ja/movie/f240b49e6f0554b3
    #エッチな0930 h0930/images/flash384x216/150297.jpg //avsox.website/ja/movie/ffad87fd194ec357
    #エッチな4610 h4610/moviepages/ori1708/images/thumb_s.jpg //avsox.website/ja/movie/e8f3651d3476c099
    #ムラムラってくる素人 muramura/images/flash384x216/150182.jpg //avsox.website/ja/movie/0744beefa8531a21
    #熟女倶楽部 jukujo/image/2182/movie_main_s.jpg //avsox.website/ja/movie/0dc4746cf43f1fec
    #Roselip roselip/movie/0654/t01.jpg //avsox.website/ja/movie/8449968519f28c4c
    #メス豚 mesubuta/gallery/160624_1061_01/images/main_f.jpg //avsox.website/ja/movie/cbf1a45a45f4024e
    #muramura muramura/moviepages/040920_834/images/str.jpg //avsox.website/ja/movie/6d66036e41e2efab
    spider_avsox_by_studio(freq)

