import re
from bs4 import BeautifulSoup
import sys
sys.path.append("..")
from crawler import DBHelper,CrawlerHelper
from crawler.shop import MGStage
#https://www.prestige-av.com/goods/goods_list.php?mode=&mid=&sort=near&word=&count=100&page=135
pcookie={'age_auth':'1'}
def spider_goodlist():
    baseurl='https://www.prestige-av.com/goods/goods_list.php?mode=&mid=&sort=near&word=&count=100&page={pageindex}'
    pageindex=1
    while True:
        print(f'page:{pageindex}')
        goodlisturl=baseurl.replace('{pageindex}',str(pageindex))
        html=CrawlerHelper.get_requests(goodlisturl,cookies=pcookie).text
        bs = BeautifulSoup(html, "html.parser")
        links=bs.find_all('a',href=re.compile('https://www.prestige-av.com/goods/goods_detail.php\?sku='))

        for link in links:
            url=link['href']
            dvdid=url[55:]
            title=link.img.get_text()

            dvdidreal=dvdid
            if dvdidreal.startswith('gooe-'):
                continue
            if dvdidreal.startswith('poh-'):
                continue
            elif dvdidreal.startswith('ctkt'):
                dvdidreal = dvdidreal.replace('ctkt', '', 1)
            elif dvdidreal.startswith('tkt'):
                dvdidreal = dvdidreal.replace('tkt', '', 1)  # GOOE
            elif dvdidreal.startswith('gooe') :
                    dvdidreal = dvdidreal.replace('gooe', '', 1)
            elif dvdidreal.startswith('sha'):
                    dvdidreal = dvdidreal.replace('sha', '', 1)
            elif dvdidreal.startswith('mgs'):
                    dvdidreal = dvdidreal.replace('mgs', '', 1)
            if DBHelper.check_dvdid_exist(dvdidreal.upper()):
                #print(f'{dvdid} existed')
                pass
            else:
                print(url)
                print(f'{dvdid} not found')
                crawler_goods_detail(dvdid)

        pageindex+=1
        if len(re.findall('次へ',html))==0:
            break
def crawler_goods_detail(dvdid):
    url=f'https://www.prestige-av.com/goods/goods_detail.php?sku={dvdid}'
    html = CrawlerHelper.get_requests(url, cookies=pcookie).text
    bs = BeautifulSoup(html, "html.parser")

    code=dvdid.upper()
    if code.startswith('CTKT'):
        code=code.replace('CTKT', '', 1)
    elif code.startswith('TKT'):
        code=code.replace('TKT', '', 1)#GOOE
    elif code.startswith('GOOE'):
        code = code.replace('GOOE', '', 1)
    elif code.startswith('SHA'):
        code = code.replace('SHA', '', 1)
    cid = code
    piccode = code




    title=bs.title.get_text().split('|')[0].strip()
    bs_detail=bs.find('div',class_='product_detail_layout_01')

    has_mgslink = False
    mgslink=bs_detail.find('a', href=re.compile(f'https://www.mgstage.com/product/product_detail/'))
    if mgslink:
        MGStage.spider_moviePage(mgslink['href'])
        return

    #<dt>収録時間：</dt>[\s]*<dd>(\d*)min</dd>
    length=None
    length=re.findall('<dt>収録時間：</dt>[\s]*<dd>(\d*)min</dd>',html)
    if len(length) > 0:
        length=length[0]
    rdate=None
    rdatetag=bs_detail.find('a',href=re.compile('/goods/goods_list.php\?mode=date&mid='))
    if rdatetag:
        rdate=rdatetag.get_text().strip()
    studio=None
    studiotag = bs_detail.find('a', href=re.compile('/goods/goods_list.php\?mode=maker&mid='))
    if studiotag:
        studio = studiotag.get_text().strip()
    label = None
    labeltag = bs_detail.find('a', href=re.compile('/goods/goods_list.php\?mode=label&mid='))
    if labeltag:
        label = labeltag.get_text().strip()
    series = None
    seriestag = bs_detail.find('a', href=re.compile('/goods/goods_list.php\?mode=series&mid='))
    if seriestag:
        series = seriestag.get_text().strip()
    if series == '写真集':
        return
    actslist = []
    actstag=bs_detail.find_all('a',href=re.compile('/goods/goods_list.php\?mode=actress&mid='))
    for acttag in actstag:

        actslist.append(acttag.get_text().strip().replace(' ',''))
    genrelist = []
    genrestag = bs_detail.find_all('a', href=re.compile('/goods/goods_list.php\?mode=genre&mid='))
    for genretag in genrestag:
        genrename=genretag.get_text().strip()
        if genrename=='グッズ':
            return
        genrelist.append(genretag.get_text().strip())
    director=None
    piccount=len(bs.find_all('img', alt=title))
    print(f'has_mgslink:{has_mgslink}')
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
    print(actslist)
    print(genrelist)

    DBHelper.save_movie(code=code, cid=cid, title=title, length=length, rdate=rdate,
                        director=director, studio=studio, label=label, series=series,
                        piccode=piccode, piccount=piccount, source=1001,
                        actresslist=actslist, genrelist=genrelist)

if __name__ == '__main__':
    #print(len('https://www.prestige-av.com/goods/goods_detail.php?sku='))
    spider_goodlist()