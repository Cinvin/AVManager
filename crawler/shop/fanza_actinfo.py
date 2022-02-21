from crawler import CrawlerHelper
import re
from bs4 import BeautifulSoup
import sqlhelper
from time import sleep
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

if __name__ == '__main__':
    #get_dmmdvd_makerid()
    update_actress_piccode()
