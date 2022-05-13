import platform
import DBHelper
import sqlhelper
import Tools
import shop.ave as ave
import shop.fanza_digital as fanza_digital
import shop.fanza_dvd as fanza_dvd
import shop.fanza_amateur as fanza_amateur
import shop.fc2 as fc2
import shop.MGStage as mgs
import shop.dmm as dmm
import studio.tokyo_hot as tokyo_hot
import studio.heyzo as heyzo
import studio._1pondo as _1pondo
import studio._10musume as _10musume
import studio.caribbeancom as caribbeancom
import studio.pacopacomama as pacopacomama
import other.av_wiki as av_wiki

# script for get new video information daily

r1=sqlhelper.fetchone('select count(1) as c from t_av')['c']
#inside:
try:
    ave.spider_new_dvdlist()
except Exception as ex:
    print(ex)
try:
    ave.spider_new_ppvlist()
except Exception as ex:
    print(ex)
try:
    heyzo.crawler_listpage()
except Exception as ex:
    print(ex)
try:
    tokyo_hot.crawler_listpage()
except Exception as ex:
    print(ex)
try:
    fc2.spider_movielist()
except Exception as ex:
    print(ex)
# try:
#     fanza_digital.spider_reserve()
#     fanza_digital.spider_newrelease()
# except Exception as ex:
#     print(ex)
# try:
#     fanza_dvd.spider_dmm_dvd_newrelease()
# except Exception as ex:
#     print(ex)
# try:
#     fanza_amateur.spider_newrelease()
# except Exception as ex:
#     print(ex)
try:
    dmm.getNewRealseDigitalVideoaItem()
except Exception as ex:
    print(ex)
try:
    dmm.getNewRealseMonoDVDItem()
except Exception as ex:
    print(ex)
try:
    dmm.getNewRealseDigitalVideocItem()
except Exception as ex:
    print(ex)
try:
    mgs.spider_reservation()
    mgs.spider_newrelease()
except Exception as ex:
    print(ex)
#other
try:
    av_wiki.get_new()
except Exception as ex:
    print(ex)
#studio
try:
    _1pondo.spider_sitemap()
except Exception as ex:
    print(ex)
try:
    _10musume.spider_sitemap()
except Exception as ex:
    print(ex)
try:
    caribbeancom.spider_sitemap()
except Exception as ex:
    print(ex)
try:
    pacopacomama.spider_sitemap()
except Exception as ex:
    print(ex)

d1=sqlhelper.fetchall('SELECT id FROM t_av a WHERE source=3 AND EXISTS (SELECT 1 FROM t_av b WHERE b.source=1 AND a.CODE=b.CODE AND a.studio_id=b.studio_id);')
for item in d1:
    DBHelper.delete_movie(item['id'])
d1=sqlhelper.fetchall('SELECT * FROM t_av a WHERE source=2 AND EXISTS (SELECT 1 FROM t_av b WHERE b.source!=2 AND a.CODE=b.CODE AND a.studio_id=b.studio_id);')
for item in d1:
    DBHelper.delete_movie(item['id'])
r2=sqlhelper.fetchone('select count(1) as c from t_av')['c']

if platform.system() == 'Darwin':
    Tools.show_notification('python', f'added {r2-r1} information')



#crontab:
#05 20 * * * ~/PythonEnvi/bin/python3 ~/PycharmProjects/AVManager/crawler/daily_crawler.py
