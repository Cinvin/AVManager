import math,random

import requests
from bs4 import BeautifulSoup
import re

import sqlhelper
from crawler import CrawlerHelper,DBHelper
from datetime import datetime
from time import sleep

javbusurl='https://www.busfan.blog/ja'
freq=0.5

def spider_javbus_movie_page(url,source2save=None):
    html = CrawlerHelper.get_requests(url)
    if html.status_code == 404:
        return
    if html.status_code != 200:
        raise Exception(f'{html.status_code} {url} 请检查')

    html = html.text
    if len(html) == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 内容为空{url}")
        return

    bs = BeautifulSoup(html, "html.parser")

    category=1
    selectedcat=bs.find('li',class_='active')
    if 'uncensored' in selectedcat.find('a')['href']:
        category=2

    # 番号+标题
    title = re.findall("<h3>(.*?)</h3>", html)
    # 番号
    code = re.findall(('品番:</span> <span style="color:#CC0000;">(.*?)</span>'), html)
    code = code[0]

    # 标题
    title = title[0]
    title = str(title).replace(code, "").strip()

    # 发行时间
    rdate=None
    findrdate = re.findall('発売日:</span> (.*?)</p>', html)
    if len(findrdate) and len(findrdate[0])> 0:
        rdate = findrdate[0]
        if rdate == '0000-00-00':
            rdate = None
    length=None
    findlength = re.findall('収録時間:</span> (\d*)分', html)
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
    actresslist = []
    for acttag in acttags:
        act = re.findall('<span>(.*?)</span>', str(acttag.contents))
        if len(act) > 0:
            actname = str(act[0])
            actresslist.append(actname)

    # 截图
    simpleimgs = bs.find_all('span', class_="sample-box")
    piccount = len(simpleimgs)

    # 番号的类型
    genretags = bs.find_all('span', class_="genre")
    genrelist = []
    for tag in genretags:
        act = re.findall('<span>(.*?)</span>', str(tag.contents))
        if tag.label is not None:
            genrelist.append(tag.get_text())
    # print(f"cid:{cid}")

    #cid
    source=18
    if source2save:
        source=source2save
        piccode=None

    print(f'code:{code}')
    print(f'category:{category}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    print(f'director:{director}')
    print(f'studio:{studio}')
    print(f'label:{label}')
    print(f'series:{series}')
    #print(f'pic:{piccode} count:{piccount}')
    print(actresslist)
    # print(histrionlist)
    print(genrelist)
    # DBHelper.save_movie(code=code, category=category, cid=None, title=title, length=length, rdate=rdate,
    #                     director=director, studio=studio, label=label, series=series,
    #                     piccode=piccode, piccount=piccount, source=source,
    #                     actresslist=actresslist, genrelist=genrelist)

def crawler_by_studio(studiokey,studioname,source2save,isuncensored=True,pageindex=1,justgetnew=True):
    cookies = {'existmag': 'all'}
    while 1 == 1:
        url = f"{javbusurl}/uncensored/studio/{studiokey}/{pageindex}"
        if not isuncensored:
            url=url.replace('uncensored/','',1)
        html = CrawlerHelper.get_requests(url, cookies=cookies).text
        bs = BeautifulSoup(html, "html.parser")
        links = bs.find_all("a", class_="movie-box")
        if not studioname:
            altertag=bs.find('div',class_='alert-success')
            if altertag:
                studioname=altertag.get_text().split(' ')[0]
        hasupdate=False
        for link in links:
            url = link["href"]
            dates = link.find_all("date")
            code = link.find_all("date")[0].get_text()
            if DBHelper.check_dvdid_exist_with_studioid(code,studio=studioname):
                continue
            hasupdate=True
            spider_javbus_movie_page(url,source2save)
        # 本页爬完 到下一页
        if not hasupdate and justgetnew:
            break
        links = bs.find_all(id="next")
        if len(links) > 0:
            pageindex += 1
            sleep(freq)
        else:
            break

def magnet(av_id,code):
    headers=CrawlerHelper.getheaders()
    url=javbusurl+'/'+code
    response = requests.get(javbusurl+'/'+code,headers=headers)
    if response.status_code != 200:
        return
    html=response.text

    gid = re.findall('var gid = (.*?);', html)[0]
    uc = re.findall('var uc = (.*?);', html)[0]
    img = re.findall("var img = '(.*?)';", html)[0]
    floor=math.floor(1e3 * random.random() + 1)

    params = {
        'gid': gid,
        'lang': 'zh',
        'img': img,
        'uc': uc,
        'floor' : floor
    }
    headers.update({'path': f'/ajax/uncledatoolsbyajax.php?gid={gid}&lang=zh&img={img}&uc={uc}floor={floor}',
                    'referer': url,})
    ajaxurl = f'{javbusurl.replace("ja", "ajax", 1)}/uncledatoolsbyajax.php'
    ajaxres = requests.get(ajaxurl,params=params,headers=headers).text
    bsajax = BeautifulSoup(ajaxres, "html.parser")
    trs = bsajax.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds)<3:
            return
        hashinfo = re.findall('magnet:\?xt=urn:btih:(.{40})', tds[0]['onclick'])[0]
        description = tds[0].find('a').get_text().strip()
        if description.endswith(' 字幕'):
            description=description[:-3]
        if description.endswith(' 高清'):
            description=description[:-3]
        size = tds[1].get_text().strip()

        date = tds[2].get_text().strip()
        if date == '0000-00-00':
            date = '1970-01-01'
        print(description, hashinfo, size, date)
        DBHelper.save_magnet(av_id, hashinfo, description, size, date)

if __name__ == '__main__':
    crawler_by_studio('3a','HEYZO',source2save=1009)