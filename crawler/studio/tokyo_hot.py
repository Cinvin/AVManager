from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper,DBHelper
from datetime import datetime
from time import sleep

#https://www.tokyo-hot.com/product/?lang=ja
def crawler_listpage(pageindex=1,get_new=True):
    while True:
        has_new=False
        url=f'https://www.tokyo-hot.com/product/?page={pageindex}&lang=ja'
        print(f'page:{url}')
        html=CrawlerHelper.get_requests(url).text
        bs = BeautifulSoup(html,'html.parser')
        boxlist=bs.find_all('li',class_='detail')
        for box in boxlist:
            code = box.find('div', class_='actor').get_text()
            code = re.findall('\(作品番号: (.*?)\)', code)[0]
            urlcid=re.findall('/product/(.*?)/',box.find('a')['href'])[0]
            if DBHelper.get_movie_obj(code,'Tokyo-Hot'):
                continue
            has_new=True
            crawler_detailpage(urlcid)
        if not has_new and get_new:
            break
        if bs.find('a',href=re.compile(f'\?page={pageindex+1}')):
            pageindex+=1
        else:
            break

def crawler_detailpage(urlcid):
    url=f'https://www.tokyo-hot.com/product/{urlcid}/?lang=ja'
    print(url)
    html = CrawlerHelper.get_requests(url).text

    bs = BeautifulSoup(html, 'html.parser')

    title=bs.title.get_text().split('|')[0].strip()

    piccode = None
    postertag = bs.find(
        poster=re.compile(f'https://my.cdn.tokyo-hot.com/media/{urlcid}/list_image/(.*?)/820x462_default.jpg'))
    if postertag:
        piccode = \
        re.findall(f'https://my.cdn.tokyo-hot.com/media/{urlcid}/list_image/(.*?)/820x462_default.jpg', postertag['poster'])[0]
    else:
        imgtag = bs.find('img',
                         src=re.compile(f'https://my.cdn.tokyo-hot.com/media/{urlcid}/list_image/(.*?)/820x462_default.jpg'))
        if imgtag:
            piccode = \
            re.findall(f'https://my.cdn.tokyo-hot.com/media/{urlcid}/list_image/(.*?)/820x462_default.jpg', imgtag['src'])[0]
    info_area=bs.find('div','infowrapper')



    acttags=info_area.find_all('a',href=re.compile('/cast/'))
    actresslist=[acttag.get_text() for acttag in acttags]
    genretags = info_area.find_all('a', href=re.compile('/product/\?type=play&filter='))
    genrelist = [genretag.get_text() for genretag in genretags]
    series=info_area.find('a',href=re.compile('/product/\?type=genre&filter='))
    if series:
        series=series.get_text()
    label = info_area.find('a', href=re.compile('/product/\?vendor='))
    if label:
        label = label.get_text()
    rdate=None
    find=re.findall('<dt>配信開始日</dt>[\s]*<dd>(.*?)</dd>',html)
    if len(find):
        rdate=find[0]
    length = None
    find = re.findall('<dt>収録時間</dt>[\s]*<dd>(.*?)</dd>', html)
    if len(find):
        lenarr = find[0].split(':')
        length = 60*int(lenarr[0])+int(lenarr[1])
    code = None
    find = re.findall('<dt>作品番号</dt>[\s]*<dd>(.*?)</dd>', html)
    if len(find):
        code = find[0]

    piccount=0

    # pic_area = bs.find('div', 'vcap')
    # if not pic_area:
    #     pic_area = bs.find('div', 'scap')
    # if pic_area:
    #     imgs=pic_area.find_all('img')
    #     piccount=len(imgs)
    #     if piccount>0:
    #         smimgsrc=imgs[0]['src']
    #         piccode+=' '+re.findall(f'https://my.cdn.tokyo-hot.com/media/{code}/(.*?)/150x150_default.jpg',smimgsrc)[0]

    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    #print(f'director:{director}')
    #print(f'studio:{studio}')
    print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount}')
    print(actresslist)
    # print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code, category=2, cid=urlcid, title=title, length=length, rdate=rdate,
                        director=None, studio='Tokyo-Hot', label=label, series=series,
                        piccode=piccode, piccount=piccount, source=1010,
                        actresslist=actresslist, genrelist=genrelist)


if __name__ == '__main__':
    crawler_listpage(get_new=False)