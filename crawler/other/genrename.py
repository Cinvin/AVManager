import re

from crawler import CrawlerHelper
from bs4 import BeautifulSoup
from model import *
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

engine = create_engine(sqlconnstr)
DBsession = sessionmaker(bind=engine)
session = DBsession()
#爬取类别的简繁日英语 方便爬取不同语言网站

def fromavmoo():
    cnurl='https://avmoo.casa/cn/genre'
    twurl = 'https://avmoo.casa/tw/genre'
    jaurl = 'https://avmoo.casa/ja/genre'
    enurl = 'https://avmoo.casa/en/genre'
    dict_ja={}
    html_ja=CrawlerHelper.get_requests(jaurl)
    bs=BeautifulSoup(html_ja.text, "html.parser")
    jatags=bs.find_all('a',class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for jatag in jatags:
        key=jatag['href'].lstrip('avmoo.casa/ja/genre/')
        name_ja=jatag.get_text()
        dict_ja[key]=name_ja
        genre = session.query(Genre).filter_by(name_ja=name_ja).first()
        if genre is None:
            gr = Genre()
            gr.name = name_ja
            gr.name_tw = name_ja
            gr.name_ja = name_ja
            session.add(gr)
            session.commit()

    html_tw = CrawlerHelper.get_requests(twurl)
    bs = BeautifulSoup(html_tw.text, "html.parser")
    twtags = bs.find_all('a', class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for twtag in twtags:
        key = twtag['href'].lstrip('avmoo.casa/tw/genre/')
        ja_name=dict_ja[key]
        tw_name=twtag.get_text()
        print(f"{ja_name}:{tw_name}")
        genre = session.query(Genre).filter_by(name_ja=ja_name).first()
        if genre is None:
            continue
        genre.name_tw=tw_name
        session.commit()

    html_cn = CrawlerHelper.get_requests(cnurl)
    bs = BeautifulSoup(html_cn.text, "html.parser")
    cntags = bs.find_all('a', class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for cntag in cntags:
        key = cntag['href'].lstrip('avmoo.casa/cn/genre/')
        ja_name = dict_ja[key]
        cn_name = cntag.get_text()
        print(f"{ja_name}:{cn_name}")
        genre = session.query(Genre).filter_by(name_ja=ja_name).first()
        if genre is None:
            continue
        genre.name_ja = ja_name
        session.commit()

    html_en = CrawlerHelper.get_requests(enurl)
    bs = BeautifulSoup(html_en.text, "html.parser")
    entags = bs.find_all('a', class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for entag in entags:
        key = entag['href'].lstrip('avmoo.casa/en/genre/')
        ja_name = dict_ja[key]
        en_name = entag.get_text()
        print(f"{ja_name}:{en_name}")
        genre = session.query(Genre).filter_by(name_ja=ja_name).first()
        if genre is None:
            continue
        genre.name_en = en_name
        session.commit()

def fromavsox():
    cnurl='https://avsox.website/cn/genre'
    twurl = 'https://avsox.website/tw/genre'
    jaurl = 'https://avsox.website/ja/genre'
    enurl = 'https://avsox.website/en/genre'
    dict_ja={}
    html_ja=CrawlerHelper.get_requests(jaurl)
    bs=BeautifulSoup(html_ja.text, "html.parser")
    jatags=bs.find_all('a',class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for jatag in jatags:
        key = re.findall('genre/(.*?)$', jatag['href'])[0]
        name_ja=jatag.get_text()
        dict_ja[key]=name_ja
        genre = session.query(Genre).filter_by(name_ja=name_ja).first()
        if genre is None:
            gr = Genre()
            gr.name = name_ja
            gr.name_tw = name_ja
            gr.name_ja = name_ja
            session.add(gr)
            session.commit()

    html_tw = CrawlerHelper.get_requests(twurl)
    bs = BeautifulSoup(html_tw.text, "html.parser")
    twtags = bs.find_all('a', class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for twtag in twtags:
        key = re.findall('genre/(.*?)$', twtag['href'])[0]
        if key not in dict_ja:
            continue
        ja_name=dict_ja[key]
        tw_name=twtag.get_text()
        if ja_name == tw_name:
            continue
        genre = session.query(Genre).filter_by(name_ja=ja_name).first()
        if genre is None or genre.name_tw!=genre.name_ja:
            continue
        print(f"tw:{ja_name}:{tw_name}")
        genre.name_tw=tw_name
        session.commit()

    html_cn = CrawlerHelper.get_requests(cnurl)
    bs = BeautifulSoup(html_cn.text, "html.parser")
    cntags = bs.find_all('a', class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for cntag in cntags:
        key = re.findall('genre/(.*?)$', cntag['href'])[0]
        if key not in dict_ja:
            continue
        ja_name = dict_ja[key]
        cn_name = cntag.get_text()
        if ja_name == cn_name:
            continue
        genre = session.query(Genre).filter_by(name_ja=ja_name).first()
        if genre is None or genre.name != genre.name_ja:
            continue
        print(f"cn:{ja_name}:{cn_name}")
        genre.name = cn_name
        session.commit()

    html_en = CrawlerHelper.get_requests(enurl)
    bs = BeautifulSoup(html_en.text, "html.parser")
    entags = bs.find_all('a', class_='col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center')
    for entag in entags:
        key = re.findall('genre/(.*?)$', entag['href'])[0]
        if key not in dict_ja:
            continue
        ja_name = dict_ja[key]
        en_name = entag.get_text()
        if ja_name == en_name:
            continue
        genre = session.query(Genre).filter_by(name_ja=ja_name).first()
        if genre is None or genre.name_en!=genre.name_ja:
            continue
        genre.name_en = en_name
        print(f"en:{ja_name}:{en_name}")
        session.commit()
def from_javlibrary():
    genrelisturl = f'http://www.k51r.com/ja/genres.php'
    html = CrawlerHelper.get_requests(genrelisturl).text
    bs = BeautifulSoup(html, "html.parser")
    genredict = {}
    genretag = bs.find_all('div', class_='genreitem')
    for genre in genretag:
        name = genre.get_text()
        code = genre.a['href'].split('=', maxsplit=1)[1]
        genredict[code]=name

    genrelisturl = f'http://www.k51r.com/cn/genres.php'
    html = CrawlerHelper.get_requests(genrelisturl).text
    bs = BeautifulSoup(html, "html.parser")
    genretag = bs.find_all('div', class_='genreitem')
    for genre in genretag:
        name = genre.get_text()
        code = genre.a['href'].split('=', maxsplit=1)[1]
        genre = session.query(Genre).filter_by(name_ja=genredict[code]).first()
        if genre is None or genre.name_ja!=genre.name:
            continue
        print(f"{genre.name}:{name}")
        genre.name = name
        session.commit()

    genrelisturl = f'http://www.k51r.com/tw/genres.php'
    html = CrawlerHelper.get_requests(genrelisturl).text
    bs = BeautifulSoup(html, "html.parser")
    genretag = bs.find_all('div', class_='genreitem')
    for genre in genretag:
        name = genre.get_text()
        code = genre.a['href'].split('=', maxsplit=1)[1]
        genre = session.query(Genre).filter_by(name_ja=genredict[code]).first()
        if genre is None or genre.name_ja != genre.name_tw:
            continue
        print(f"{genre.name_tw}:{name}")
        genre.name_tw = name
        session.commit()

    genrelisturl = f'http://www.k51r.com/en/genres.php'
    html = CrawlerHelper.get_requests(genrelisturl).text
    bs = BeautifulSoup(html, "html.parser")
    genretag = bs.find_all('div', class_='genreitem')
    for genre in genretag:
        name = genre.get_text()
        code = genre.a['href'].split('=', maxsplit=1)[1]
        genre = session.query(Genre).filter_by(name_ja=genredict[code]).first()
        if genre is None or genre.name_ja != genre.name_en:
            continue
        print(f"{genre.name_en}:{name}")
        genre.name_en = name
        session.commit()

if __name__ == '__main__':
    #fromavmoo()
    fromavsox()
    #from_javlibrary()