import urllib.parse
from bs4 import BeautifulSoup
import re
from crawler import CrawlerHelper
import sqlhelper
from crawler import DBHelper
from model import Actress

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
                print(f'{actname} {link}')
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
        href=act['href']
        found=re.findall('/article=actress/id=(.*?)/',href)
        if len(found)==0:
            found = re.findall('/article=actor/id=(.*?)/', href)
        if len(found):
            actname=act.get_text()
            actliststr.replace(actname, '')
            if '／' in actname and mainname in actname:
                actname=mainname
            else:
                actname = actname.split(' ※', 1)[0]
                actname = actname.split('*', 1)[0]
                actname = actname.split('(', 1)[0].strip()
                actname = actname.split('（',1)[0].strip()
            if actname not in act_contactdict:
                act_contactdict[actname]=found[0]

    actnamesplit=actliststr.split('／')
    for act in actnamesplit:
        actname = act.split('※',1)[0]
        actname = actname.split('*', 1)[0]
        actname = actname.split('(', 1)[0]
        actname = actname.split('（', 1)[0].strip()
        if actname not in act_contactdict:
            act_contactdict[actname] = None
    if mainname not in act_contactdict:
        return
    print(mainname)
    print(act_contactdict)
    save_actinfo(act_contactdict,mainname)
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

if __name__=='__main__':
    spider_actresslist()