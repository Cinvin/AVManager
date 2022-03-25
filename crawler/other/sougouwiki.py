import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper
import sqlhelper
from crawler import DBHelper
from model import Actress
from crawler.shop.fanza_dvd import crawler_dmmdvd_page

def encode(strcode):
    return urllib.parse.quote(strcode, safe="/", encoding="euc_jp", errors=None).lower()
def decode(strcode):
    return urllib.parse.unquote(strcode, encoding="euc_jp")

def spider_actresslist():
    pagelist=['女優ページ一覧', '女優ページ一覧：か行',
              '女優ページ一覧：さ行','女優ページ一覧：た行',
              '女優ページ一覧：な行', '女優ページ一覧：は行',
              '女優ページ一覧：ま行',
                '女優ページ一覧：や行',
              '女優ページ一覧：ら・わ行', 'グラビアアイドル一覧']

    urllist=['http://sougouwiki.com/d/'+encode(a) for a in pagelist]
    actressesurls=[]
    for url in urllist:
        html=CrawlerHelper.get_requests(url).text
        bs = BeautifulSoup(html, "html.parser")
        content_blocks=bs.find_all('div', id=re.compile('content_block_(.*?)-body'))
        for content_block in content_blocks:
            lis=content_block.find_all('li')
            for li in lis:
                acttag=li.find('a',href=re.compile('http://sougouwiki.com/d/'))
                if not acttag:
                    continue
                actname=acttag.get_text()
                if sqlhelper.fetchone('select 1 from t_actress a where exists(select 1 from t_actress b where a.mainid=b.id and b.actname=%s)',actname):
                    continue
                link = acttag['href']
                spider_actresspage(link)

def spider_actresspage(url):
    html = CrawlerHelper.get_requests(url).text
    bs = BeautifulSoup(html, "html.parser")
    h3=bs.find('h3',id='content_1')
    if not h3:
        return
    mainname = bs.find('h2').get_text().strip()
    if '(' in mainname or '（' in mainname or ' ' in mainname:
        return
    actnames=h3.find_all('a')
    act_contactdict = {}
    actliststr = h3.get_text()

    for act in actnames:
        href = act['href']
        found = re.findall('/article=actress/id=(.*?)/', href)
        if len(found) == 0:
            found = re.findall('/article=actor/id=(.*?)/', href)
        if len(found):
            actname = act.get_text()
            actliststr.replace(actname, '')
            if '／' in actname and mainname in actname:
                actname = mainname
            else:
                actname = actname.split(' ※', 1)[0]
                actname = actname.split('*', 1)[0]
                actname = actname.split('(', 1)[0].strip()
                actname = actname.split('（', 1)[0].strip()
            if actname not in act_contactdict:
                act_contactdict[actname] = found[0]

    actnamesplit = actliststr.split('／')
    for act in actnamesplit:
        actname = act.split('※', 1)[0]
        actname = actname.split('*', 1)[0]
        actname = actname.split('(', 1)[0]
        actname = actname.split('（', 1)[0].strip()
        if actname not in act_contactdict:
            act_contactdict[actname] = None
    if mainname not in act_contactdict:
        return
    print(mainname)
    print(act_contactdict)
    save_actinfo(act_contactdict, mainname)

    twittertags=bs.find_all('a',href=re.compile('twitter.com/.*?'))
    twitter=None
    for twittertag in twittertags:
        if twittertag.parent.name != 'del':
            twittertext=twittertag['href'].rstrip('/')
            if twittertext=='https://twitter.com/share':
                continue
            twitter=re.findall('twitter.com/(.*?)$',twittertext)[0]
            if '/' in twitter:
                twitter = twitter.split('/')[0]
            break

    #social media
    instagramtags = bs.find_all('a', href=re.compile('instagram.com/*?'))
    instagram = None
    for instagramtag in instagramtags:
        if instagramtag.parent.name != 'del':
            instagramtext = instagramtag['href'].rstrip('/')
            instagram = re.findall('instagram.com/(.*?)$', instagramtext)[0]
            if '/' in instagram:
                instagram = instagram.split('/')[0]
            break
    print(mainname,twitter,instagram)
    result=sqlhelper.fetchone('select count(1) as c from t_actress where actname=%s',mainname)
    if result and result['c']==1:
        if twitter:
            sqlhelper.execute('update t_actress set twitter=%s where actname=%s',twitter,mainname)
        if instagram:
            sqlhelper.execute('update t_actress set instagram=%s where actname=%s',instagram,mainname)
def save_actinfo(act_contactdict,mainname):
    for k,v in act_contactdict.items():
        if v:
            try:
                int(v)
            except:
                return
    if len(act_contactdict)>0:
        if mainname not in act_contactdict:
            return
        mainfanzaid=act_contactdict[mainname]
        actmain_obj = None
        if mainfanzaid:
            actmain_obj = DBHelper.session.query(Actress).filter_by(fanzaid=mainfanzaid).first()
            if actmain_obj:
                actmain_obj.actname=mainname
                actmain_obj.mainid=None
                DBHelper.session.commit()
        if not actmain_obj:
            actmain_obj = DBHelper.session.query(Actress).filter_by(actname=mainname).first()
            if not actmain_obj:
                return
        for actname,fanzaid in act_contactdict.items():
            if actname==mainname:
                continue
            # if fanzaid:
            #     DBHelper.save_actress_fanzaid(actname,fanzaid)
            DBHelper.save_actress_mainid(actname, actmain_obj.id)

def add_movie_actress(source,cid,actname):
    avid=sqlhelper.fetchone('select id from t_av where cid=%s and source=%s',cid,source)
    if not avid:
        return
    actid=sqlhelper.fetchone('select id from t_actress where actname=%s',actname)
    if not actid:
        sqlhelper.execute('insert into t_actress(actname) values(%s)',actname)
        actid = sqlhelper.fetchone('select id from t_actress where actname=%s', actname)
    if not sqlhelper.fetchone('select 1 from t_av_actress where av_id=%s and actress_id=%s',avid['id'],actid['id']):
        sqlhelper.execute('insert into t_av_actress(av_id,actress_id) values(%s,%s)', avid['id'],actid['id'])
        print(f'add actinfo:{cid} {actname}')
    else:
        print(f'exists actinfo:{cid} {actname}')

def add_movie_actress_dvdid(dvdid,source,actname):
    avid=sqlhelper.fetchone('select id from t_av where code=%s and source=%s',dvdid,source)
    if not avid:
        return
    actid=sqlhelper.fetchone('select id from t_actress where actname=%s',actname)
    if not actid:
        sqlhelper.execute('insert into t_actress(actname) values(%s)',actname)
        actid = sqlhelper.fetchone('select id from t_actress where actname=%s', actname)
    if not sqlhelper.fetchone('select 1 from t_av_actress where av_id=%s and actress_id=%s',avid['id'],actid['id']):
        sqlhelper.execute('insert into t_av_actress(av_id,actress_id) values(%s,%s)', avid['id'],actid['id'])
        print(f'add actinfo:{dvdid} {actname}')
    else:
        print(f'exists actinfo:{dvdid} {actname}')

def seriestablepageinfo(url,studio=None):
    #http://sougouwiki.com/d/%a5%b9%a5%d1%a5%a4%a5%b9%a5%d3%a5%b8%a5%e5%a5%a2%a5%eb
    html = CrawlerHelper.get_requests(url).text
    bs = BeautifulSoup(html, "html.parser")
    tables = bs.find_all('table', id=re.compile('content_block_(.*?)'))
    for table in tables:
        dict_index={'no':0,'photo':1,'title':2,'actress':3,'release':4}
        thead = table.find('thead')
        if not thead:
            continue
        ths = thead.find_all('th')
        for i in range(0,len(ths)):
            thtext=ths[i].get_text().lower()
            if thtext == 'no':
                dict_index['no']=i
            elif thtext == 'photo':
                dict_index['photo']=i
            elif thtext == 'title':
                dict_index['title']=i
            elif thtext == 'subtitle':
                dict_index['title'] = i
                dict_index['subtitle'] = i
            elif thtext == 'actress':
                dict_index['actress']=i
            elif thtext == 'release':
                dict_index['release']=i
        #print(dict_index)
        tbody = table.find('tbody')
        trs=tbody.find_all('tr')
        for tr in trs:
            tds=tr.find_all('td')
            if len(tds)<5:
                continue
            code=tds[dict_index['no']].get_text()
            code=code.strip(' |?')

            imgobj=tds[dict_index['photo']].find('img')
            if not imgobj:
                continue
            imgurl=imgobj['src']
            source=1
            cid=None
            find_cid=re.findall('pics.dmm.(co.jp|com)/digital/video/(.*?)/', imgurl)
            if len(find_cid):
                cid = find_cid[0][1]
            elif len(re.findall('pics.dmm.(co.jp|com)/digital/amateur/(.*?)/', imgurl))>0:
                cid = re.findall('pics.dmm.(co.jp|com)/digital/amateur/(.*?)/', imgurl)[0][1]
                source = 4
            elif len(re.findall('image.mgstage',imgurl))>0:
                cid=code
                source = 2
            else:
                find_cid = re.findall('pics.dmm.(co.jp|com)/mono/movie/adult/(.*?)/', imgurl)
                if len(find_cid):
                    cid = find_cid[0][1]
                    source=3
                else:
                    find_cid = re.findall('pics.dmm.(co.jp|com)/mono/movie/idol/(.*?)/', imgurl)
                    if len(find_cid):
                        cid = find_cid[0][1]
                        source = 3
                    else:
                        find_cid = re.findall('pics.dmm.(co.jp|com)/mono/movie/(.*?)/', imgurl)
                        if len(find_cid):
                            cid = find_cid[0][1]
                            source = 3
            if not cid:
                continue

            title = tds[dict_index['title']].get_text().strip()
            if len(title.strip('-'))==0:
                continue

            actresses=[]
            actress_area=tds[dict_index['actress']]
            acts_nolink = actress_area.find_all('span',style='color:gray;background-color:yellow')
            for act_nolink in acts_nolink:
                actname=act_nolink.get_text().strip()
                if len(actname)==0:
                    continue
                actresses.append(actname)
            acts_haslink = actress_area.find_all('a')
            for act_haslink in acts_haslink:
                actname = act_haslink.get_text().strip()
                if actname == '?':
                    continue
                actresses.append(act_haslink.get_text())

            date = tds[dict_index['release']].get_text().strip()
            if len(date.strip('-'))==0:
                date=None
            # if DBHelper.get_movie_obj(code=code,studio=studio):
            #     continue
            # if DBHelper.get_movie_by_cid(source=source,cid=cid):
            #     continue
            print(code,source,cid,title,actresses,date)
            if len(actresses)>0:
                try:
                    DBHelper.save_movie_actress(cid=cid,source=source,actresslist=actresses)
                except Exception as ex:
                    print(ex)

            # if studio:
            #     DBHelper.save_movie(code=code,title=title, studio=studio,rdate=date,cid=cid,piccode=cid,source=source,actresslist=actresses)
            # else:
            #     DBHelper.save_movie(code=code, title=title, rdate=date, cid=cid, piccode=cid, source=source,
            #                         actresslist=actresses)


def fanza_amteur_actress():
    #http://sougouwiki.com/d/%c1%b4%a5%bf%a5%a4%a5%c8%a5%eb%b0%ec%cd%f7%28FANZA%c6%b0%b2%e8%29
    html = CrawlerHelper.get_requests('http://sougouwiki.com/d/%c1%b4%a5%bf%a5%a4%a5%c8%a5%eb%b0%ec%cd%f7%28FANZA%c6%b0%b2%e8%29').text
    bs = BeautifulSoup(html, "html.parser")
    content_blocks = bs.find_all('div', id=re.compile('content_block_(.*?)-body'))
    for content_block in content_blocks:
        links=content_block.find_all('a',href=re.compile('http://sougouwiki.com/d/(.*?)'))
        for link in links:
            print(f'page: {link.get_text()}')
            seriestablepageinfo(link['href'])

def msgtage_amteur_actress():
    html = CrawlerHelper.get_requests('http://sougouwiki.com/d/%c1%b4%a5%bf%a5%a4%a5%c8%a5%eb%b0%ec%cd%f7%28MGS%c6%b0%b2%e8%29').text
    bs = BeautifulSoup(html, "html.parser")
    content_blocks = bs.find_all('div', id=re.compile('content_block_(.*?)-body'))
    for content_block in content_blocks:
        links=content_block.find_all('a',href=re.compile('http://sougouwiki.com/d/(.*?)'))
        for link in links:
            print(f'page: {link.get_text()}')
            seriestablepageinfo(link['href'])

if __name__=='__main__':
    spider_actresslist()
    # fanza_amteur_actress()
    # msgtage_amteur_actress()