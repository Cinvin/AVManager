from bs4 import BeautifulSoup
import re
import CrawlerHelper
import minnano
from datetime import datetime,timedelta
from time import sleep
import sys
from crawler import DBHelper
sys.path.append("..")
from model import *
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

# setting
freq = 1 # second
avmoourl = 'avmoo.casa'

def spider_avmoo_movie_page(url, session):
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

    if code == "-000":
        return

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
    studio = bs.find_all('a', href=re.compile("studio"))
    if len(studio) > 0:
        studio = studio[0].get_text()
    else:
        studio = None
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
    actslist = []
    for acttag in acttags:
        act = re.findall('<span>(.*?)</span>', str(acttag.contents))
        if len(act) > 0:
            actname = str(act[0])
            actslist.append(actname)
            if act is None:
                minnano.updateactressinfo(actname, session)
            actpiccode = re.findall('/actjpgs/(.*?).jpg', str(acttag.div.img["src"]))
            if len(actpiccode) > 0 and actpiccode[0] != "printing":
                # 演员图片代号
                actitem = session.query(Actress).filter_by(actname=actname).first()
                if actitem is None:
                    actitem = Actress()
                    actitem.actname = actname
                    session.add(actitem)
                actitem.piccode = actpiccode[0]
                session.commit()
    simpleimgs = bs.find_all('a', class_="sample-box")
    piccount = len(simpleimgs)

    piccode = re.findall("jp.netcdn.space/digital/video/(.*?)/", html)[0]

    # 番号的类型
    genretags = bs.find_all('span', class_="genre")
    genrelist = []
    for tag in genretags:
        genre = tag.get_text()
        if len(genre) > 0:
            genrelist.append(genre)

    # 保存
    DBHelper.save_movie(code=code,title=title, length=length,rdate=rdate,
                        director=director, studio=studio,label=label, series=series,
                        piccode=piccode, piccount=piccount,source=1,
                        actslist=actslist, genrelist=genrelist)


def spider_avmoo_newmovie(second, session, xmlpageindex=1):
    link = f"https://{avmoourl}/ja/sitemap-movie-(index).xml"

    while True:
        print(f"avmoo 第{xmlpageindex}个movie xml")
        html = CrawlerHelper.get_requests(link.replace('(index)', str(xmlpageindex)))
        if html.status_code != 200:
            raise Exception(f'{html.status_code} {link} 请检查')

        html = html.text

        bs = BeautifulSoup(html, "xml")

        dateupdated = datetime.now()
        dateupdated -= timedelta(days=30)
        urltags = bs.find_all("url")
        if len(urltags) == 0:
            break
        for urltag in urltags:
            lastmod = urltag.find('lastmod').contents[0]
            lastmod = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%SZ")
            if lastmod<dateupdated:
                continue
            loc=urltag.find('loc').contents[0]
            movielink = 'https:'+loc
            spider_avmoo_movie_page(movielink, session)
            sleep(freq)
        xmlpageindex += 1
        sleep(freq)

def spider_avmoo_by_studio(second):
    link = f"https://{avmoourl}/ja/sitemap-studio-(index).xml"
    index = 2
    while True:
        html = CrawlerHelper.get_requests(link.replace('(index)', str(index)))
        if html.status_code != 200:
            raise Exception(f'{html.status_code} {link} 请检查')

        html = html.text

        bs = BeautifulSoup(html, "xml")

        links = bs.find_all("loc")
        if len(links) == 0:
            break
        start = 0
        if index == 1:
            start = 1593
        for i in range(start, len(links)):
            linktag = links[i]
            movielink = linktag.get_text()
            print(f"spider_avmoo_by_studio 爬 第{index}页的{i}个 url: {movielink}")
            crawler_movielist_page(movielink, second)
            sleep(second)
        index += 1


def crawler_movielist_page(pageurl, second):
    pageindex = 1
    # 页面循环
    while 1 == 1:
        print(f"crawler_movielist_page 爬第{pageindex}页")
        html = CrawlerHelper.get_requests(f"{pageurl}/page/{pageindex}").text
        bs = BeautifulSoup(html, "html.parser")
        if pageindex == 1:
            actinfo = bs.find_all("div", class_="avatar-box")
            if len(actinfo) > 0:
                acttext = str(actinfo[0])
                actname = re.findall('<span class="pb-10">(.*?)</span>', acttext)[0]
                if "(" in actname:
                    actname = actname.split("(")[0]
                actpiccode = re.findall('/actjpgs/(.*?).jpg', acttext)[0]
                if "print" in actpiccode:
                    actpiccode = None
                birth = re.findall('<p>生年月日: (.*?)</p>', acttext)
                if len(birth) > 0:
                    birth = birth[0]
                else:
                    birth = None
                height = re.findall('<p>身長: (.*?)cm</p>', acttext)
                if len(height) > 0:
                    height = height[0]
                else:
                    height = None
                cups = re.findall('<p>ブラのサイズ: (.*?)</p>', acttext)
                if len(cups) > 0:
                    cups = cups[0]
                else:
                    cups = None
                bust = re.findall('<p>バスト: (.*?)cm</p>', acttext)
                if len(bust) > 0:
                    bust = bust[0]
                else:
                    bust = None
                waist = re.findall('<p>ウエスト: (.*?)cm</p>', acttext)
                if len(waist) > 0:
                    waist = waist[0]
                else:
                    waist = None
                hips = re.findall('<p>ヒップ: (.*?)cm</p>', acttext)
                if len(hips) > 0:
                    hips = hips[0]
                else:
                    hips = None
                birthplace = re.findall('<p>出身地: (.*?)</p>', acttext)
                if len(birthplace) > 0:
                    birthplace = birthplace[0]
                else:
                    birthplace = None
                hobby = re.findall('<p>趣味: (.*?)</p>', acttext)
                if len(hobby) > 0:
                    hobby = hobby[0]
                else:
                    hobby = None
                datas = [actname, birth, height, cups, bust, waist, hips, birthplace, hobby, actpiccode]
                # sqlhelper.save_actresses_info(datas)
        boxlist = bs.find_all("a", class_="movie-box")
        for box in boxlist:
            url = box["href"]
            code = box.find_all("date")[0].get_text()

            src = box.find_all("img")[0]["src"]
            piccode = re.findall("/digital/video/(.*?)/", src)
            if piccode[0] == "printing":
                continue
            else:
                # 爬！
                spider_avmoo_movie_page('https:'+url, session)
                sleep(second)
        # 本页爬完 到下一页
        findnext = re.findall("次へ ", html)
        if len(findnext) > 0:
            pageindex = pageindex + 1
            sleep(second)
        else:
            break


def search_by_keyword(keyword, second, session, issearchcode=False):
    pageindex = 1
    while 1 == 1:
        url = f"https://{avmoourl}/ja/search/{keyword}/page/{pageindex}"
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 爬取{url}")
        html = CrawlerHelper.get_requests(url).text
        bs = BeautifulSoup(html, "html.parser")
        boxlist = bs.find_all("a", class_="movie-box")
        for box in boxlist:
            url = box["href"]
            code = box.find_all("date")[0].get_text()
            date = box.find_all("date")[1].get_text()
            src = box.find_all("img")[0]["src"]
            piccode = re.findall("/digital/video/(.*?)/", src)
            # if not sqlhelper.is_movie_exist(piccode):
            # 爬！
            if issearchcode and code != keyword:
                continue
            spider_avmoo_movie_page('https:'+url, session)
            sleep(second)
        # 本页爬完 到下一页
        findnext = re.findall("次へ ", html)
        if len(findnext) > 0:
            pageindex += 1
            sleep(second)
        else:
            break


if __name__ == '__main__':

    engine = create_engine(sqlconnstr)
    DBsession = sessionmaker(bind=engine)
    session = DBsession()

    spider_avmoo_newmovie(freq, session)


# 图片
#
# 大图https://jp.netcdn.space/digital/video/ipx00590/ipx00590pl.jpg
# https://pics.dmm.co.jp/digital/video/ssni00973/ssni00973pl.jpg
# 小图https://jp.netcdn.space/digital/video/ipx00590/ipx00590jp-4.jpg
# https://pics.dmm.co.jp/digital/video/ssni00975/ssni00975jp-6.jpg
# 头像
# https://pics.dmm.co.jp/mono/actjpgs/otosiro_sayaka.jpg
# https://avmoo.casa/cn/movie/fc7850d1cbf6f50a