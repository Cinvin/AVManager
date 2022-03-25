from datetime import datetime
import re
from concurrent.futures.thread import ThreadPoolExecutor
import sqlhelper
from crawler import CrawlerHelper, DBHelper
from bs4 import BeautifulSoup
from model import *

def updateactressinfo(actname):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{actname} start")
    pageurl = "http://www.minnano-av.com/search_result.php?search_scope=actress&search_word=actressname&search=+Go+"
    url = pageurl.replace("actressname", actname)
    html = CrawlerHelper.get_requests(url)

    acttext = None


    if html.url.startswith("http://www.minnano-av.com/search_result.php?"):
        bs_actlist=BeautifulSoup(html.text, "html.parser")
        actatags=bs_actlist.find_all('a',href=re.compile(f'actress\d*.html\?{actname}'))
        for acttag in actatags:
            if acttag.get_text()==actname:
                acturl=acttag['href']
                htmlactpage = CrawlerHelper.get_requests(f'http://www.minnano-av.com/{acturl}')
                if len(re.findall(f'<title>{actname}（',htmlactpage.text))>0:
                    acttext=htmlactpage.text
                    break
    else:
        acttext = html.text

    if not acttext:
        print(f'not found {actname}')
        return

    bs = BeautifulSoup(acttext, "html.parser")

    # 生日
    birth = re.findall('<span>生年月日</span><p>(\d*年\d*月\d*)日', acttext)
    if len(birth) > 0:
        birth = birth[0]
        birth = datetime.strptime(birth, '%Y年%m月%d').date()
    else:
        birth = None

    # 身材
    bodytext = re.findall('<span>サイズ</span><p>(.*?)</p>', acttext)
    # T157 / B84(<a href="actress_list.php?cup=C">Cカップ</a>) / W56 / H82 / S24
    if len(bodytext) > 0:
        bodytext = bodytext[0]
    else:
        bodytext = ""

    height = re.findall('T(\d+)', bodytext)
    if len(height) > 0:
        height = height[0]
    else:
        height = None

    cups = re.findall('cup=(.)"', bodytext)
    if len(cups) > 0:
        cups = cups[0]
    else:
        cups = None
    bust = re.findall('B(\d+)', bodytext)
    if len(bust) > 0:
        bust = bust[0]
    else:
        bust = None
    waist = re.findall('W(\d+)', bodytext)
    if len(waist) > 0:
        waist = waist[0]
    else:
        waist = None
    hips = re.findall('H(\d+)', bodytext)
    if len(hips) > 0:
        hips = hips[0]
    else:
        hips = None

    blood_type_tag = bs.find('a',href=re.compile('actress_list.php\?blood_type='))
    bloodtype=None
    if blood_type_tag:
        bloodtype=re.findall('blood_type=(.*?)$',blood_type_tag['href'])[0]


    bptag = bs.find_all('a', href=re.compile("place"))
    if len(bptag) > 0:
        birthplace = bptag[0].get_text()
        if len(birthplace) == 0:
            birthplace = None
    else:
        birthplace = None

    hobby = re.findall('<span>趣味・特技</span><p>(.*?)</p>', acttext)
    if len(hobby) > 0 and len(hobby[0]) > 0:
        hobby = hobby[0]
    else:
        hobby = None

    twittertags = bs.find_all('a', href=re.compile('twitter.com/.*?'))
    twitter = None
    for twittertag in twittertags:
        twittertext = twittertag['href'].rstrip('/')
        if twittertext != 'https://twitter.com/share':
            twitter = re.findall('twitter.com/(.*?)$', twittertext)[0]
            if '/' in twitter:
                twitter = twitter.split('/')[0]
            break
    instagramtags = bs.find_all('a', href=re.compile('instagram.com/*?'))
    instagram = None
    for instagramtag in instagramtags:
        if instagramtag.parent.name != 'del':
            instagramtext = instagramtag['href'].rstrip('/')
            instagram = re.findall('instagram.com/(.*?)$', instagramtext)[0]
            if '/' in instagram:
                instagram = instagram.split('/')[0]
            break

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", actname,birth,height,cups,bust,waist,hips,bloodtype,birthplace,hobby,f'twitter@{twitter}',f'instagram@{instagram}')
    session = DBHelper.get_session()
    actress = session.query(Actress).filter(Actress.actname == actname).first()
    if actress is None:
        return
        # actress=Actress()
        # session.add(actress)

    actress.actname=actname
    if birth and not actress.birthday:
        actress.birthday=birth
    if height and not actress.height:
        actress.height=height
    if cups and not actress.cup:
        actress.cup=cups
    if bust and not actress.bust:
        actress.bust=bust
    if waist and not actress.waist:
        actress.waist=waist
    if hips and not actress.hips:
        actress.hips=hips
    if birthplace and not actress.birthplace:
        actress.birthplace=birthplace
    if hobby and not actress.hobby:
        actress.hobby=hobby
    if bloodtype and not actress.bloodtype:
        actress.bloodtype=bloodtype
    if twitter and not actress.twitter:
        actress.twitter=twitter
    if instagram and not actress.instagram:
        actress.instagram=instagram
    session.commit()
    session.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{actname} end")

def updates():
    d1 = sqlhelper.fetchall(
        'SELECT actname,id from t_actress a WHERE EXISTS (SELECT 1 FROM t_av_actress b where b.actress_id=a.id) ORDER BY id')

    resultcount = len(d1)
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(0, resultcount):
            if sqlhelper.fetchone('select count(1) as c from t_actress where actname=%s', d1[i]['actname'])['c'] == 1:
                t.submit(updateactressinfo, d1[i]['actname'])

    for item in d1:
        if sqlhelper.fetchone('select count(1) as c from t_actress where actname=%s',item['actname'])['c']==1:
            updateactressinfo(item['actname'])
def main():
    result=sqlhelper.fetchall("SELECT actname from t_actress a WHERE actname>=%s and fanzaid is null and EXISTS (SELECT 1 FROM t_av_actress b where b.actress_id=a.id) ORDER BY actname",
                              '')
    resultcount=len(result)
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(0, resultcount):
            t.submit(updateactressinfo, result[i]['actname'])

if __name__ == '__main__':
    updates()
    #updateactressinfo('堺希美',DBHelper.session)