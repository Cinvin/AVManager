from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper,DBHelper

#https://www.heyzo.com/listpages/all_1.html
def crawler_listpage(pageindex=1,get_new=True):
    while True:
        has_new=False
        url=f'https://www.heyzo.com/listpages/all_{pageindex}.html'
        print(f'page:{url}')
        html=CrawlerHelper.get_requests(url).text
        bs = BeautifulSoup(html,'html.parser')
        linklist=bs.find_all('a',href=re.compile('/moviepages/(.*?)/index.html'))
        for link in linklist:
            cid=re.findall('/moviepages/(.*?)/index.html',link['href'])[0]
            code=f'HEYZO-{cid}'
            if DBHelper.check_dvdid_exist_with_studioid(code,'HEYZO'):
                continue
            has_new=True
            crawler_detailpage(cid)
        if not has_new and get_new:
            break
        if bs.find('a',href=re.compile(f'all_{pageindex+1}.html')):
            pageindex+=1
        else:
            break

def crawler_detailpage(cid):
    url=f'https://www.heyzo.com/moviepages/{cid}/index.html'
    print(url)
    html = CrawlerHelper.get_requests(url).text

    bs = BeautifulSoup(html, 'html.parser')

    code=f'HEYZO-{cid}'
    title=bs.h1.get_text().split('-',1)[0].strip()

    rdate=None
    table_release_day = bs.find('tr', class_='table-release-day')
    tds=table_release_day.find_all('td')
    for td in tds:
        tdtext=td.get_text().strip()
        if len(re.findall('(\d*-\d*-\d*)',tdtext))>0:
            rdate=tdtext
    if not rdate:
        #"dateCreated":"2021-08-27"
        findrdate = re.findall('"dateCreated":"(\d*-\d*-\d*)"', html)
        if len(findrdate):
            rdate = findrdate[0]
    if rdate:
        rdate=rdate[:10]
    actresslist=[]
    table_actor=bs.find('tr',class_='table-actor')
    actors=table_actor.find_all('a',href=re.compile('listpages/actor'))
    for actor in actors:
        actresslist.append(actor.get_text())

    series = None
    table_series = bs.find('tr', class_='table-series')
    seriesobj = table_series.find('a', href=re.compile('listpages/series'))
    if seriesobj:
        series=seriesobj.get_text()

    genrelist=[]
    table_tag_keyword_smalls=bs.find_all('tr',class_='table-tag-keyword-small')
    for table_tag_keyword_small in table_tag_keyword_smalls:
        genres=table_tag_keyword_small.find_all('a',href=re.compile('/search/'))
        for genre in genres:
            genrelist.append(genre.get_text())

    length = None
    find = re.findall('"full":"(\d\d:\d\d:\d\d)"', html)
    if len(find):
        lenarr = find[0].split(':')
        length = 60*int(lenarr[0])+int(lenarr[1])

    piccode=cid
    piccount=len(re.findall(f'/member/contents/3000/{piccode}/gallery/thumbnail_(.*?).jpg',html))
    print(f'code:{code}')
    print(f'title:{title}')
    print(f'length:{length}')
    print(f'rdate:{rdate}')
    #print(f'director:{director}')
    #print(f'studio:{studio}')
    #print(f'label:{label}')
    print(f'series:{series}')
    print(f'pic:{piccode} count:{piccount}')
    print(actresslist)
    # print(histrionlist)
    print(genrelist)
    DBHelper.save_movie(code=code, category=2, cid=None, title=title, length=length, rdate=rdate,
                        director=None, studio='HEYZO', label=None, series=series,
                        piccode=piccode, piccount=piccount, source=1009,
                        actresslist=actresslist, genrelist=genrelist)


if __name__ == '__main__':
    crawler_listpage()