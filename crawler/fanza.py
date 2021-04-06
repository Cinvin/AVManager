import CrawlerHelper
import re
from bs4 import BeautifulSoup
import sqlhelper
from time import sleep

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
        url=f"https://www.dmm.co.jp/digital/videoa/-/actress/=/keyword={keyword}/page=pageindex/"
        pageindex=1
        while True:
            html=CrawlerHelper.get_requests(url.replace("pageindex",str(pageindex)))
            if "/age_check/" in html.url:
                hrefs = re.findall('<a href="(.*?)"', str(html.text))
                for href in hrefs:
                    if "declared=yes" in href:
                        html = CrawlerHelper.get_requests(href)
            print(html.url)
            bs = BeautifulSoup(html.text, "html.parser")
            imgs = bs.find_all('img',src=re.compile("https://pics.dmm.co.jp/mono/actjpgs/medium/"))
            for img in imgs:
                name = img['alt']
                codes = re.findall('https://pics.dmm.co.jp/mono/actjpgs/medium/(.*?).jpg', str(img['src']))
                if len(codes)>0:
                    sqlhelper.execute("update t_actress set piccode=%s where actname=%s",codes[0], name)
                    print(f"update {name} {codes[0]}")
            terminals=bs.find_all('li', class_="terminal")
            nextflag=False
            for terminal in terminals:
                if "次へ" in terminal.get_text():
                    nextflag=True
            if nextflag:
                pageindex+=1
            else:
                break
            sleep(0.5)