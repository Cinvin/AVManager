from concurrent.futures import ThreadPoolExecutor

from crawler import CrawlerHelper, DBHelper
import re
from bs4 import BeautifulSoup
import sqlhelper
from time import sleep
from model import Actress
dmmcookie={'age_check_done':'1'}
def update_actress_piccode():
    '''
    获取演员头像代号 访问dmm需科学上网
    :return:
    '''
    keywords=['a', 'i', 'u', 'e', 'o',
              'ka', 'ki', 'ku', 'ke', 'ko',
              'sa', 'si', 'su', 'se', 'so',
              'ta', 'ti', 'tu', 'te', 'to',
              'na', 'ni', 'nu', 'ne', 'no',
              'ha', 'hi', 'hu', 'he', 'ho',
              'ma', 'mi', 'mu', 'me', 'mo',
              'ya',       'yu',       'yo',
              'ra', 'ri', 'ru', 're', 'ro',
              'wa']
    for keyword in keywords:
        #https://www.dmm.co.jp/mono/dvd/-/actress/=/keyword={keyword}/page=pageindex/
        #https://www.dmm.co.jp/digital/videoa/-/actress/=/keyword={keyword}/page=pageindex/
        #https://www.dmm.co.jp/rental/-/actress/=/keyword=a/
        urls=[f"https://www.dmm.co.jp/mono/dvd/-/actress/=/keyword={keyword}/page=pageindex/",
              f"https://www.dmm.co.jp/digital/videoa/-/actress/=/keyword={keyword}/page=pageindex/",
              f"https://www.dmm.co.jp/rental/-/actress/=/keyword={keyword}/"]
        for url in urls:
            pageindex=1
            while True:
                print(url)
                html=CrawlerHelper.get_requests(url.replace("pageindex",str(pageindex)),cookies=dmmcookie)
                bs = BeautifulSoup(html.text, "html.parser")
                act_box=bs.find('div',class_='act-box')
                if not act_box:
                    act_box=bs
                atags = act_box.find_all('a',href=re.compile("/article=actress/"))
                for atag in atags:
                    img=atag.img
                    if not img:
                        continue
                    name = img['alt']#(digital)
                    if 'dvd' in html.url:
                        name = atag.get_text()#(dvd)
                    codes = re.findall('https://pics.dmm.co.jp/mono/actjpgs/medium/(.*?).jpg', str(img['src']))
                    if "rental" in url:
                        codes = re.findall('https://pics.dmm.co.jp/mono/actjpgs/thumbnail/(.*?).jpg', str(img['src']))
                    id = re.findall('/id=(.*?)/', str(atag['href']))
                    if len(codes)>0:
                        fechresult=sqlhelper.fetchone('select 1 from t_actress where fanzaid=%s',id[0])
                        if fechresult:
                            sqlhelper.execute("update t_actress set piccode=%s where fanzaid=%s",
                                              codes[0],id[0])
                        else:
                            sqlhelper.execute("update t_actress set piccode=%s,fanzaid=%s where actname=%s",
                                              codes[0],id[0], name)
                        print(name, codes[0], id[0])
                terminals=bs.find_all('li', class_="terminal")
                nextflag=False
                for terminal in terminals:
                    if "次へ" in terminal.get_text():
                        nextflag=True
                if nextflag:
                    pageindex+=1
                else:
                    break
def get_dmmdvd_makerid():
    makeridlist = []
    ja50 = ['a', 'i', 'u', 'e', 'o',
                'ka', 'ki', 'ku', 'ke', 'ko',
                'sa', 'si', 'su', 'se', 'so',
                'ta', 'ti', 'tu', 'te', 'to',
                'na', 'ni', 'nu', 'ne', 'no',
                'ha', 'hi', 'hu', 'he', 'ho',
                'ma', 'mi', 'mu', 'me', 'mo',
                'ya', 'yu', 'yo',
                'ra', 'ri', 'ru', 're', 'ro',
                'wa']
    for ja in ja50:
        makerlisturls=[f'https://www.dmm.co.jp/digital/videoa/-/maker/=/keyword={ja}/',
                        f'https://www.dmm.co.jp/mono/dvd/-/maker/=/keyword={ja}/',
                       f'https://www.dmm.co.jp/rental/-/maker/=/keyword={ja}/']
        for makerlisturl in makerlisturls:
            makerlisthtml=CrawlerHelper.get_requests(makerlisturl,cookies=dmmcookie)
            bs = BeautifulSoup(makerlisthtml.text, "html.parser")
            atags=bs.find_all('a',href=re.compile('/article=maker/id='))
            for atag in atags:
                makerid=re.findall('/article=maker/id=(\d*)/',atag['href'])
                if len(makerid)==0:
                    continue
                makerid=makerid[0]
                makername=atag.get_text().strip()
                if len(makerid)>0 and len(makername) > 0:
                    fechresult = sqlhelper.fetchone('select 1 from t_studio where name=%s', makername)
                    if fechresult:
                        sqlhelper.execute("update t_studio set fanzaid=%s where name=%s",
                                          makerid, makername)
                        print(f"update {makername} {makerid}")
                    else:
                        sqlhelper.execute("insert into t_studio (name,fanzaid) values (%s,%s)",
                                          makername, makerid)
                        print(f"insert {makername} {makerid}")

def update_actress_info_by_id(act_fanzaid):
    html = CrawlerHelper.get_requests(f'https://actress.dmm.co.jp/-/detail/=/actress_id={act_fanzaid}/', cookies=dmmcookie)
    if html.status_code==404:
        return
    bs = BeautifulSoup(html.text, "html.parser")
    actname=bs.find('meta',property='og:title')['content']
    actressimg=bs.find('img',src=re.compile('https://pics\.dmm\.co\.jp/mono/actjpgs/.*?\.jpg'))
    avatar=None
    piccode=None
    if actressimg:
        piccode=re.findall('https://pics\.dmm\.co\.jp/mono/actjpgs/(.*?)\.jpg',actressimg['src'])[0]
        if piccode=='printing':
            piccode=None
        else:
            avatar=actressimg['src']
    p_list_profile=bs.find('dl',class_='p-list-profile')
    dds=p_list_profile.find_all('dd')
    birth = dds[0].get_text().strip()
    bloodtype=dds[2].get_text().strip()
    body = dds[3].get_text().strip()
    birthplace = dds[4].get_text().strip()
    hobby = dds[5].get_text().strip()
    height, bust, cup, waist, hips=(None,None,None,None,None)
    if birth=='---':
        birth=None
    else:
        birth=re.sub('年|月','-',birth)[:-1]
    if body != '---':
        findheight=re.findall('T(\d*)cm',body)
        if len(findheight)>0:
            height=findheight[0]
        findbust = re.findall('B(\d*)cm', body)
        if len(findbust) > 0:
            bust = findbust[0]
        findcup = re.findall('\(([A-Z])カップ\)', body)
        if len(findcup) > 0:
            cup = findcup[0]
        findwaist = re.findall('W(\d*)cm', body)
        if len(findwaist) > 0:
            waist = findwaist[0]
        findhips = re.findall('H(\d*)cm', body)
        if len(findhips) > 0:
            hips = findhips[0]
    if bloodtype=='---':
        bloodtype=None
    if birthplace=='---':
        birthplace=None
    if hobby=='---':
        hobby=None
    print(act_fanzaid,actname,piccode,birth,bloodtype,height,bust,cup,waist,hips,birthplace,hobby)
    session = DBHelper.get_session()
    actress = session.query(Actress).filter(Actress.fanzaid == act_fanzaid).first()
    if not actress:
        actress = session.query(Actress).filter(Actress.actname == actname , Actress.fanzaid is None).first()
    if not actress:
        actress=Actress()
        actress.actname=actname
        session.add(actress)

    actress.actname = actname
    if birth and not actress.birthday:
        actress.birthday = birth
    if height and not actress.height:
        actress.height = height
    if bloodtype and not actress.bloodtype:
        actress.bloodtype=bloodtype
    if cup and not actress.cup:
        actress.cup = cup
    if bust and not actress.bust:
        actress.bust = bust
    if waist and not actress.waist:
        actress.waist = waist
    if hips and not actress.hips:
        actress.hips = hips
    if birthplace and not actress.birthplace:
        actress.birthplace = birthplace
    if hobby and not actress.hobby:
        actress.hobby = hobby
    if piccode and not actress.piccode:
        actress.piccode = piccode
    if avatar and not actress.avatar:
        actress.avatar = avatar
    if not actress.fanzaid:
        actress.fanzaid = act_fanzaid
    session.commit()
    session.close()
    #fanza_digital.spider_byactid(actfanzaid=act_fanzaid)

def update_actinfo():
    result=sqlhelper.fetchall("SELECT fanzaid from t_actress WHERE fanzaid>=%s and fanzaid is not null ORDER BY fanzaid",
                              0)
    resultcount=len(result)
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(0, resultcount):
            t.submit(update_actress_info_by_id, result[i]['fanzaid'])


if __name__ == '__main__':
    update_actinfo()

