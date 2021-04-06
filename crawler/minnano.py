from datetime import datetime
import re
import requests

import CrawlerHelper
from bs4 import BeautifulSoup
from model import *

def updateactressinfo(actname, session):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{actname} start")
    pageurl = "https://www.minnano-av.com/search_result.php?search_scope=actress&search_word=actressname&search=+Go+"
    url = pageurl.replace("actressname", actname)
    html = CrawlerHelper.get_requests(url)
    if html.url.startswith("https://www.minnano-av.com/search_result.php?"):
        return
    acttext=html.text
    bs = BeautifulSoup(acttext, "html.parser")
    nametext = bs.h1.find("span").get_text()
    piccode = None
    if r"/" in nametext:
        piccode = nametext.split(r"/")[-1].strip()
        piccode = piccode.replace(" ", "_").lower()
        pichtml = requests.get(f"https://pics.dmm.co.jp/mono/actjpgs/{piccode}.jpg", stream=True)
        if pichtml.url == "https://pics.dmm.com/mono/movie/n/now_printing/now_printing.jpg":
            othercode = piccode.replace("tsu", "tu")
            othercode = othercode.replace("shi", "si")
            othercode = othercode.replace("chi", "ci")
            othercode = othercode.replace("fu", "hu")
            if othercode != piccode:
                pichtml = requests.get(f"https://pics.dmm.co.jp/mono/actjpgs/{othercode}.jpg", stream=True)
                if pichtml.url != "https://pics.dmm.com/mono/movie/n/now_printing/now_printing.jpg":
                    piccode=othercode
                else:
                    piccode=None
            else:
                piccode = None

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

    actress = session.query(Actress).filter(Actress.actname == actname).first()
    if actress is None:
        actress=Actress()
        session.add(actress)

    actress.actname=actname
    if birth is not None:
        actress.birthday=birth
    if height is not None:
        actress.height=height
    if cups is not None:
        actress.cup=cups
    if bust is not None:
        actress.bust=bust
    if waist is not None:
        actress.waist=waist
    if hips is not None:
        actress.hips=hips
    if birthplace is not None:
        actress.birthplace=birthplace
    if hobby is not None:
        actress.hobby=hobby
    if piccode is not None:
        actress.piccode=piccode
    session.commit()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{actname} end")
