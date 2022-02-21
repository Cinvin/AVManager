import re
from bs4 import BeautifulSoup
from crawler import CrawlerHelper, DBHelper
from crawler.shop import fanza_digital, fanza_amateur


def get_dvd_id_in_R18(keyword):
    url=f'https://www.r18.com/common/search/searchword={keyword}/'
    html = CrawlerHelper.get_requests(url, cookies={'lg': 'zh'})
    if html is None or html.status_code==404:
        return None
    html=html.text
    bs=BeautifulSoup(html, "html.parser")
    atags=bs.find_all('a', href=re.compile(f'https://www.r18.com/videos/vod/movies/detail/-/id={keyword}/'))

    if len(atags) != 1:
        return None
    return atags[0].find('img')['alt']

def spider_by_sitemap_R18_dvdid():
    url='https://www.r18.com/sitemap.xml'
    xml=CrawlerHelper.get_requests(url)

    bs = BeautifulSoup(xml.text, "xml")
    sitemaplinks = bs.find_all("loc")
    for sitemaplink in sitemaplinks:
        sl=sitemaplink.get_text()
        findxml=re.findall('https://www.r18.com/sitemap/detail_(\d*).xml',sl)
        if len(findxml)>0:
            data=CrawlerHelper.get_requests(sl)
            videoabs = BeautifulSoup(data.text, "xml")
            urls = videoabs.find_all("url")
            del data
            del videoabs
            print(sl)
            urllength=len(urls)
            while len(urls)>0:
                urlitem=urls.pop()
                loc=urlitem.loc
                video=urlitem.video
                if not loc:
                    continue
                loc=loc.get_text()
                cid = re.findall('https://www.r18.com/videos/vod/movies/detail/-/id=(.*?)/', loc)
                if len(cid)>0:
                    cid = cid[0]
                    m = DBHelper.get_movie_by_cid(1, cid)
                    if not m:
                        fanza_digital.crawler_dmmmoive(cid)
                        m = DBHelper.get_movie_by_cid(1, cid)
                        if not m:
                            print(f'not exists:{cid} https://www.r18.com/videos/vod/movies/detail/-/id={cid}/')
                    continue

                cid = re.findall('https://www.r18.com/videos/vod/amateur/detail/-/id=(.*?)/', loc)
                if len(cid) > 0:
                    cid = cid[0]
                    m = DBHelper.get_movie_by_cid(4, cid)
                    if not m:
                        fanza_amateur.crawler_dmm_amateur_page(cid)
                        m = DBHelper.get_movie_by_cid(4, cid)
                        if not m:
                            print(f'not exists:{cid} https://www.r18.com/amateur/vod/movies/detail/-/id={cid}/')
                    continue




if __name__ == '__main__':
    #spider_by_sitemap_R18_dvdid()
    print(get_dvd_id_in_R18('td043dvaj00461'))
