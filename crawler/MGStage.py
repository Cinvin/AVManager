import string

from bs4 import BeautifulSoup
import re
import CrawlerHelper
from datetime import datetime
from time import sleep
import sys
from crawler import DBHelper
sys.path.append("..")
import gzip

# setting
freq = 2 # second

#sitemap: https://www.mgstage.com/product_detail_sitemap1.xml.gz

def spider_by_sitemap(freq:int):
    sitemapurl='https://www.mgstage.com/product_detail_sitemap{num}.xml.gz'
    for i in range(1,4):
        print(f'crawler sitemap page {str(i)}')
        data = CrawlerHelper.get_requests(sitemapurl.replace("{num}", str(i)))
        data = gzip.decompress(data.content).decode('utf8')
        bs = BeautifulSoup(data, "xml")
        links = bs.find_all("loc")
        del data
        del bs
        for link in links:
            url=link.get_text()
            piccode = re.findall('/product/product_detail/(.*?)/', url)[0]
            if not DBHelper.check_dvdid_exist(piccode.lstrip(string.digits)):
                spider_moviePage(link.get_text())
                sleep(freq)

def spider_by_maker(freq:int):
    sitemapurl='https://www.mgstage.com/maker_sitemap.xml.gz'
    data = CrawlerHelper.get_requests(sitemapurl)
    data = gzip.decompress(data.content).decode('utf8')
    bs = BeautifulSoup(data, "xml")
    links = bs.find_all("loc")
    del data
    del bs
    aaaa=True
    for link in links:
        link=link.get_text()
        if 'Maybit' in link:
            aaaa=False
            continue
        if aaaa:
            continue
        urlbase = link+'&page={page}'
        pageindex=1
        while 1==1:
            url=urlbase.replace('{page}',str(pageindex))
            html = gethtml(url)
            bs = BeautifulSoup(html, "html.parser")
            studio=bs.find('input',class_='b_image_word_ids')["value"][:-2]
            print(f"studio:{studio} page:{str(pageindex)}")

            mgscode = re.findall(f'https://image.mgstage.com/images/(.*?)/', html)
            if len(mgscode) > 0:
                DBHelper.save_mgscode(studio, mgscode[0])

            linktags=bs.find_all('a', href=re.compile('/product/product_detail/'))
            for linktag in linktags:
                titletag=linktag.find('p')
                if titletag is None:
                    continue
                url = linktag["href"]
                title=titletag.get_text().split(' ')[0]
                print(title)
                return
                piccode = re.findall('/product/product_detail/(.*?)/',url)[0]
                avitem=DBHelper.check_movie_exist_with_title(piccode.lstrip(string.digits), title)
                if avitem is None:
                    spider_moviePage('https://www.mgstage.com'+url)
                    sleep(freq)
                elif avitem.source == 1:
                    #如果dmm图挂了换成mgs的
                    dmmpicurl=f'http://pics.dmm.co.jp/digital/video/{avitem.piccode}/{avitem.piccode}ps.jpg'
                    img = CrawlerHelper.get_requests(dmmpicurl, is_stream=True)
                    if "printing" in img.url:
                        DBHelper.change_to_mgs_pic(piccode, studio)
            if len(linktags)==0:
                break
            pageindex=1+pageindex
            sleep(freq)
        sleep(freq)

#https://www.mgstage.com/product/product_detail/022SGSR-079/
def spider_moviePage(url):
    html = CrawlerHelper.get_requests(url, cookies={'adc':'1'})
    if html is None:
        html = CrawlerHelper.get_requests(url, cookies={'adc':'1'})
    if html is None:
        return
    if html.status_code != 200:
        raise Exception(f'{html.status_code} 请检查 {url}')
    html = gethtml(url)
    if len(html) == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 内容为空{url}")
        return
    bs = BeautifulSoup(html, "html.parser")
    # 标题

    title = bs.find("h1",class_="tag")
    if title:
        title = title.get_text().strip()
    else:
        title = bs.find("title").get_text().strip()
        title = re.findall('「(.*)」',title)[0]

    # piccode=bs.find_all('img',class_='enlarge_image')[0]['src']
    # piccode=piccode.lstrip('https://image.mgstage.com/images/').rstrip('.jpg')
    # piccode=piccode.replace('/pf_o1_','/*_').replace('/pb_p_', '/*_')
    piccode=re.findall('https://www.mgstage.com/product/product_detail/(.*?)/',url)[0]

    code = None
    rdate = None
    rdate2 = None
    length = None
    director = None
    studio = None
    label = None
    series = None
    actslist = []
    genrelist =[]
    trs=bs.find_all("tr")
    for tr in trs:
        tkey = tr.find_all("th")
        if len(tkey)>0:
            tkey=tkey[0].get_text()
        else:
            continue
        tval = tr.find_all("td")
        if len(tval) == 0:
            continue
        tval=tval[0]
        if tkey == '品番：':
            code=tval.get_text().strip().lstrip(string.digits)
        elif tkey == '出演：':
            acttags = tval.find_all('a')
            for acttag in acttags:
                actslist.append(acttag.get_text().strip())
        elif tkey == 'メーカー：':
            studio=tval.get_text().strip()
        elif tkey == '収録時間：':
            length = tval.get_text().rstrip('min')
        elif tkey == '商品発売日：':
            rdate = tval.get_text()
            if rdate=='DVD未発売':
                rdate=None
        elif tkey == '配信開始日：':
            rdate2 = tval.get_text()
        elif tkey == 'シリーズ：':
            series = tval.get_text().strip()
            if series=='': series=None
        elif tkey == 'レーベル：':
            label = tval.get_text().strip()
            if label=='': label=None
        elif tkey == 'ジャンル：':
            genretags=tval.find_all('a')
            for tag in genretags:
                genre = tag.get_text().strip()
                if len(genre) > 0:
                    genrelist.append(genre)

    if rdate is None and rdate2 is not None and rdate2 != 'DVD未発売':
        rdate=rdate2

    pics=bs.find_all('img', src=re.compile('/cap_'))
    piccount=len(pics)



    DBHelper.save_movie(code=code, title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=piccount, source=2,
                        actslist=actslist, genrelist=genrelist)

    # https://image.mgstage.com/images/(.*?)/300maan/001/pb_e_300maan-001.jpg
    mgscode = re.findall(f'https://image.mgstage.com/images/(.*?)/{ piccode.lower().replace("-","/") }/', html)
    if len(mgscode)>0:
        DBHelper.save_mgscode(studio,mgscode[0])

def gethtml(url):
    html = CrawlerHelper.get_requests(url, cookies={'adc': '1'})
    if html is None:
        sleep(freq)
        html = CrawlerHelper.get_requests(url, cookies={'adc': '1'})
    if html is None:
        return None
    if html.status_code != 200:
        raise Exception(f'{html.status_code} 请检查 {url}')
    return html.text


if __name__ == '__main__':
    spider_by_sitemap(freq=freq)