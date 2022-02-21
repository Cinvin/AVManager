import sqlhelper
from crawler import CrawlerHelper,DBHelper
import re
from time import sleep
from bs4 import BeautifulSoup

url='https://qq9741.com'

def search_movie_javbook_bypage(second,pagestart:int=1,pageend:int=0):
    index = pagestart
    #https://qq9741.com/serchinfo_censored/topicsbt/topicsbt_2288.htm
    #https://qq9741.com/serchinfo_uncensored/topicsbt/topicsbt_609.htm
    while 1 == 1:
        pageurl = f"{url}/serchinfo_uncensored/topicsbt/topicsbt_{index}.htm"
        print(pageurl)
        link = pageurl.replace("{index}", str(index))
        pagehtml = CrawlerHelper.get_requests(link).text
        sleep(second)
        bs = BeautifulSoup(pagehtml, "html.parser")
        # boxlist = bs.find_all("div", class_="Po_topic")
        boxlist = bs.find_all("div", class_="Po_u_topic")
        for boxtag in boxlist:
            #src=boxtag.find_all("img")[0]["src"]
            #piccode=re.findall("pics.dmm.co.jp/digital/video/(.*?)/",src)
            #piccode=piccode[0]

            code=boxtag.find_all("font",color='#CC0000')[0].get_text()
            code=str(code).split(' /')[0]

            link=boxtag.find("a")["href"]
            #if not sqlhelper.is_movie_exist(piccode):
            get_magnet(link)
            sleep(second)
        if pageend>0 and pageend==index:
            break
        index += 1
        if not bs.find('a',href=re.compile(f'_{index}.htm')):
            break


def get_magnet(url):
    html = CrawlerHelper.get_requests(url).text

    codefind = re.findall('番號：</b><font color="#A63600"><a href=.*?>(.*?)</a>', html)
    if len(codefind)==0:
        codefind = re.findall('番號：</b><font color="#A63600">(.*?)</font>', html)
    code=codefind[0]

    av_id=None
    resav=DBHelper.check_dvdid_exist(code)
    if resav:
        av_id=resav.id
    dmmpiccode = re.findall("pics.dmm.co.jp/digital/video/(.*?)/", html)
    if len(dmmpiccode)>0:
        dmmpiccode=dmmpiccode[0]
        id=sqlhelper.fetchone('select id from t_av where source=1 and piccode=%s',dmmpiccode)
        if id:
            av_id=id['id']
    if not av_id:
        return
    print(f'av_id:{av_id} code:{code}')
    bs = BeautifulSoup(html, "html.parser")
    magnetlist=[]
    infos = bs.find_all('div', class_='dht_dl_title_content')
    magnet_descriptions=[]
    for info in infos:
        content_bt_url=info.find('span',class_='content_bt_url')
        linktag = content_bt_url.find('a')
        magnet_descriptions.append(linktag.text)

    infos = bs.find_all('div', class_='dht_dl_size_content')
    magnet_sizes = []
    for info in infos:
        magnet_sizes.append(info.text)

    infos = bs.find_all('div', class_='dht_dl_date_content')
    magnet_dates = []
    for info in infos:
        magnet_dates.append(info.text)
    magnet_hashinfos = []
    infos = re.findall("\+reurl\('(.*?)'\)",html)
    for info in infos:
        magnet_hashinfos.append(reurl(info))
    for i in range(0,len(magnet_hashinfos)):
        if 'email' in magnet_descriptions[i]:
            continue
        print(magnet_descriptions[i],magnet_sizes[i],magnet_dates[i],magnet_hashinfos[i])
        DBHelper.save_magnet(av_id,magnet_hashinfos[i],magnet_descriptions[i],magnet_sizes[i],magnet_dates[i])


#js of reurl
# function reurl(a)
# {
#     var b='';
#     var c=csplit(a,8).split('\r\n');
#     for(var i=0;i<(c.length-1);i++)
#     {
#         b=b+String.fromCharCode((parseInt(c[i],2)-10).toString(10))
#     }
#     return b
# }
# function csplit(a,b,c)
# {
#     b=parseInt(b,10)||76;
#     c=c||'\r\n';
#     if(b<1)
#     {
#         return false
#     }
#     return a.match(new RegExp(".{0,"+b+"}","g")).join(c)
# }

def reurl(code):
    splited = csplit(code)
    return ''.join(list(map(lambda i: chr(int(i, 2) - 10), splited)))

def csplit(code):
    res = []
    for i in range(0,40):
        res.append(code[0+i*8:8+i*8])
    return res
if __name__ == '__main__':
    search_movie_javbook_bypage(0.5,1)