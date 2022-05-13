import re
import string
from datetime import datetime,timedelta

import requests
import json

import model
import sqlhelper
from crawler import DBHelper, Tools, CrawlerHelper
import time

#getapiid from https://affiliate.dmm.com/api/guide/
api_id='ezuc1BvgM0f74KV4ZMmS'
affiliate_id='sakuradite-999'

class DMMAPI():
    #baseurl='https://api.dmm.com/affiliate/v3/ItemList?api_id=ezuc1BvgM0f74KV4ZMmS&affiliate_id=sakuradite-999'
    def __init__(self,api_id,affiliate_id):
        self.api_id=api_id
        self.affiliate_id = affiliate_id
        self.baseurl=f'https://api.dmm.com/affiliate/v3/*?api_id={api_id}&affiliate_id={affiliate_id}'
    def _postdata(self,url,data):
        response=requests.post(url,data)
        html=response.text
        return json.loads(html)
    def _getresult(self,url):
        print(url)
        html=CrawlerHelper.get_requests(url).text
        return json.loads(html)
    def getItemList(self,site='FANZA',service=None,floor=None, hits=None,offset=None, sort=None,
                    keyword=None,cid=None,article=None,article_id=None,
                    gte_date=None,lte_date=None,mono_stock=None,
                    output='json',callback=None):
        '''

        :param site:
        :param service:
        :param floor:
        :param hits:
        :param offset:
        :param sort:
        :param keyword:
        :param cid:
        :param article: 女優：女優：actress
作者：author
ジャンル：genre
シリーズ：series
メーカー：maker
        :param article_id:	上述收窄项的ID（可从各个搜索API获取）
        :param gte_date:
        :param lte_date:
        :param mono_stock:
        :param output:
        :param callback:
        :return:
        '''
        #https://affiliate.dmm.com/api/v3/itemlist.html
        ItemListurl=self.baseurl.replace('*', 'ItemList', 1)
        if site:
            ItemListurl += f'&site={site}'
        if service:
            ItemListurl += f'&service={service}'
        if floor:
            ItemListurl += f'&floor={floor}'
        if hits:
            ItemListurl += f'&hits={hits}'
        if offset:
            ItemListurl += f'&offset={offset}'
        if sort:
            ItemListurl += f'&sort={sort}'
        if keyword:
            ItemListurl += f'&keyword={keyword}'
        if cid:
            ItemListurl += f'&cid={cid}'
        if article:
            ItemListurl += f'&article={article}'
        if article_id:
            ItemListurl += f'&article_id={article_id}'
        if gte_date:
            ItemListurl += f'&gte_date={gte_date}'
        if lte_date:
            ItemListurl += f'&lte_date={lte_date}'
        if mono_stock:
            ItemListurl += f'&mono_stock={mono_stock}'
        if output:
            ItemListurl += f'&output={output}'
        if callback:
            ItemListurl += f'&callback={callback}'
        return self._getresult(ItemListurl)

    def getFloorList(self):
        # floorids:
        # 43:動画.ビデオ(digital.videoa)
        # 44:動画.素人(digital.videoc)
        # 45:動画.成人映画(digital.nikkatsu)
        # 46:動画.アニメ動画(digital.anime)
        # 71:DVDレンタル.月額レンタル(rental.rental_dvd)
        # 72:DVDレンタル.単品レンタル(rental.ppr_dvd)
        # 74:通販.DVD(mono.dvd)
        return self._getresult(self.baseurl.replace('*', 'FloorList', 1))

    def getActressSearch(self,initial=None,actress_id=None,keyword=None,
                    gte_bust=None,lte_bust=None,
                    gte_waist=None,lte_waist=None,
                    gte_hip=None,lte_hip=None,
                    gte_height=None,lte_height=None,
                    gte_birshday=None,lte_birthday=None,
                    hits=None,offset=None,sort=None,
                    output='json',callback=None):
        '''
        女優情報
        :param initial: 50音をUTF-8で指定
        :param actress_id:
        :param keyword:
        :param gte_bust:gte_bust=90ならバスト90cm以上、
        :param lte_bust:lte_bust=90ならバスト90cm以下
        :param gte_waist:
        :param lte_waist:
        :param gte_hip:
        :param lte_hip:
        :param gte_height:
        :param lte_height:
        :param gte_birshday:yyyymmddの形式で指定
        :param lte_birthday:yyyymmddの形式で指定
        :param hits:	初期値：20　最大：100
        :param offset:	初期値：1
        :param sort:名前昇順：name
名前降順：-name
バスト昇順：bust
バスト降順：-bust
ウエスト昇順：waist
ウエスト降順：-waist
ヒップ昇順：hip
ヒップ降順：-hip
身長昇順：height
身長降順：-height
生年月日昇順：birthday
生年月日降順：-birthday
女優ID昇順：id
女優ID降順：-id
        :param output:
        :param callback:
        :return:
        '''
        # https://affiliate.dmm.com/api/v3/actresssearch.html
        ActressSearchurl = self.baseurl.replace('*', 'ActressSearch', 1)
        if initial:
            ActressSearchurl += f'&initial={initial}'
        if actress_id:
            ActressSearchurl += f'&actress_id={actress_id}'
        if keyword:
            ActressSearchurl += f'&keyword={keyword}'
        if gte_bust:
            ActressSearchurl += f'&gte_bust={gte_bust}'
        if lte_bust:
            ActressSearchurl += f'&lte_bust={lte_bust}'
        if gte_waist:
            ActressSearchurl += f'&gte_waist={gte_waist}'
        if lte_waist:
            ActressSearchurl += f'&lte_waist={lte_waist}'
        if gte_hip:
            ActressSearchurl += f'&gte_hip={gte_hip}'
        if lte_hip:
            ActressSearchurl += f'&lte_hip={lte_hip}'
        if gte_height:
            ActressSearchurl += f'&gte_height={gte_height}'
        if lte_height:
            ActressSearchurl += f'&lte_height={lte_height}'
        if gte_birshday:
            ActressSearchurl += f'&gte_birshday={gte_birshday}'
        if lte_birthday:
            ActressSearchurl += f'&lte_birthday={lte_birthday}'
        if hits:
            ActressSearchurl += f'&hits={hits}'
        if offset:
            ActressSearchurl += f'&offset={offset}'
        if sort:
            ActressSearchurl += f'&sort={sort}'
        if output:
            ActressSearchurl += f'&output={output}'
        if callback:
            ActressSearchurl += f'&callback={callback}'
        return self._getresult(ActressSearchurl)

    def getGenreSearch(self,floor_id,initial=None,hits=None,offset=None,output='json',callback=None):
        '''
        ジャンル一覧
        :param floor_id:フロア検索APIから取得可能なフロアID(floorlist)
        :param initial:
        :param hits:
        :param offset:
        :param output:
        :param callback:
        :return:
        '''
        # https://affiliate.dmm.com/api/v3/genresearch.html
        GenreSearchurl = self.baseurl.replace('*', 'GenreSearch', 1)
        GenreSearchurl += f'&floor_id={floor_id}'
        if initial:
            GenreSearchurl += f'&initial={initial}'
        if hits:
            GenreSearchurl += f'&hits={hits}'
        if offset:
            GenreSearchurl += f'&offset={offset}'
        if output:
            GenreSearchurl += f'&output={output}'
        if callback:
            GenreSearchurl += f'&callback={callback}'
        return self._getresult(GenreSearchurl)

    def getSeriesSearch(self,floor_id,initial=None,hits=None,offset=None,output='json',callback=None):
        '''
        ジャンル一覧
        :param floor_id:フロア検索APIから取得可能なフロアID(floorlist)
        :param initial:
        :param hits:
        :param offset:
        :param output:
        :param callback:
        :return:
        '''
        # https://affiliate.dmm.com/api/v3/seriessearch.html
        SeriesSearchurl = self.baseurl.replace('*', 'SeriesSearch', 1)
        SeriesSearchurl += f'&floor_id={floor_id}'
        if initial:
            SeriesSearchurl += f'&initial={initial}'
        if hits:
            SeriesSearchurl += f'&hits={hits}'
        if offset:
            SeriesSearchurl += f'&offset={offset}'
        if output:
            SeriesSearchurl += f'&output={output}'
        if callback:
            SeriesSearchurl += f'&callback={callback}'
        return self._getresult(SeriesSearchurl)

def getNewRealseDigitalVideoaItem():
    dmm = DMMAPI(api_id, affiliate_id)
    hits=100
    offset=1
    datelimit = datetime.now()
    datelimit -= timedelta(days=31)

    gte_date = datelimit.strftime('%Y-%m-%d') + 'T00:00:00'
    while True:
        print(f'offset:{offset}')
        result = dmm.getItemList(service='digital', floor='videoa', gte_date=gte_date, hits=hits, offset=offset, sort='date')['result']
        total_count = result.get('total_count',0)
        items = result['items']
        for item in items:
            save_videoa_to_server(item)
        offset = offset+hits
        if total_count<=offset:
            break

def getNewRealseMonoDVDItem():
    dmm = DMMAPI(api_id, affiliate_id)
    hits=100
    offset=1
    datelimit = datetime.now()
    datelimit += timedelta(days=31)

    lte_date = datelimit.strftime('%Y-%m-%d') + 'T00:00:00'
    lte_date = '2013-03-23T00:00:00'
    while True:
        print(f'offset:{offset}')
        result = dmm.getItemList(service='mono', floor='dvd', hits=hits, offset=offset, lte_date=lte_date, sort='date')['result']
        total_count = result.get('total_count',0)
        items = result['items']
        for item in items:
            if 'volume' not in item or 'maker' not in item['iteminfo'] or 'maker_product' not in item or 'jancode' not in item:
                continue
            code=item['maker_product']
            cid=item['content_id']
            title=item['title']
            print(code,item.get('date', None))
            studio=item['iteminfo']['maker'][0]['name']

            queryobj=DBHelper.check_cid_exist(cid)
            if not queryobj:
                queryobj=DBHelper.check_cid_exist(
                    cid.replace(cid.rstrip(string.digits), cid.rstrip(string.digits) + '00', 1))
            if queryobj:
                if queryobj.code!=code and queryobj.title == item['title']:
                    queryobj.code = code
                    DBHelper.session.commit()
                continue
            if DBHelper.check_dvdid_exist_with_studioid(code, studio=studio, studio_id=None):
                continue
            if DBHelper.check_movie_exist_with_title_similar(code, item['title']):
                continue
            titleav = DBHelper.check_title_exist_with_studio(title, studio=studio)
            if titleav:
                if titleav.source != 3:
                    continue
            piccount = len(item['sampleImageURL']['sample_s']['image']) if 'sampleImageURL' in item else 0
            piccode=cid
            if piccount>0:
                sampleurl=item['sampleImageURL']['sample_s']['image'][0]
                samplepiccode = re.findall('https://pics.dmm.co.jp/digital/video/(.*?)/', sampleurl)[0]
                if samplepiccode != piccode:
                    piccode = piccode +' '+ samplepiccode
                    piccodeav = DBHelper.check_piccode_exist(samplepiccode)
                    if piccodeav:
                        continue
            actresslist = []
            actress_fanzaidlist = {}
            for actress in item['iteminfo'].get('actress',[]):
                actresslist.append(actress['name'])
                actress_fanzaidlist[actress['id']] = actress['name']
            genrelist = [genre['name'] for genre in item['iteminfo'].get('genre',[])]

            avobj=DBHelper.get_movie_by_cid(3,item['content_id'])
            if avobj:
                if avobj.piccount < piccount:
                    avobj.piccount = piccount
                    avobj.piccode = piccode
                    DBHelper.session.commit()
                if avobj.code != code:
                    avobj.code = code
                    DBHelper.session.commit()
                if avobj.actresses.count()>=len(actresslist):
                    continue
            DBHelper.save_movie(code=code,
                                cid=item['content_id'],
                                title=item['title'], length=item['volume'], rdate=item.get('date', None),
                                director=item['iteminfo']['director'][0]['name'] if 'director' in item['iteminfo'] else None,
                                studio=item['iteminfo']['maker'][0]['name'] if 'maker' in item['iteminfo'] else None,
                                label=item['iteminfo']['label'][0]['name'] if 'label' in item['iteminfo'] else None,
                                series=item['iteminfo']['series'][0]['name'] if 'series' in item['iteminfo'] else None,
                                piccode=piccode,
                                piccount=piccount,
                                source=3,
                                actresslist=[], genrelist=genrelist, histrionlist=[],
                                actress_fanzaidlist=actress_fanzaidlist, histrion_fanzaidlist={})
        offset=offset+hits
        if total_count <= offset:
            break

def getNewRealseDigitalVideocItem():
    #getcount=500
    dmm = DMMAPI(api_id, affiliate_id)
    hits=100
    offset=1
    datelimit = datetime.now()
    datelimit -= timedelta(days=31)

    gte_date = datelimit.strftime('%Y-%m-%d') + 'T00:00:00'
    while True:
        print(f'offset:{offset}')
        result = dmm.getItemList(service='digital', floor='videoc',gte_date=gte_date, hits=hits, offset=offset, sort='date')['result']
        total_count = result.get('total_count',0)
        items = result['items']
        for item in items:
            save_videoc_to_server(item)
        offset = offset + hits
        if total_count<=offset:
            break

def getDigitalVideoaItemById(cid):
    dmm = DMMAPI(api_id, affiliate_id)
    result=dmm.getItemList(service='digital', floor='videoa', cid=cid)['result']
    items = result['items']
    for item in items:
        save_videoa_to_server(item)

def getDigitalVideocItemById(cid):
    dmm = DMMAPI(api_id, affiliate_id)
    result=dmm.getItemList(service='digital', floor='videoc', cid=cid)['result']
    items = result['items']
    for item in items:
        save_videoc_to_server(item)

def getAllActress():
    dmm = DMMAPI(api_id, affiliate_id)
    hits = 100
    offset = 11801
    while True:
        print(f'offset:{offset}')
        result = dmm.getActressSearch(hits=hits, offset=offset, sort='-id')['result']
        total_count = result.get('total_count', 0)
        for item in result['actress']:
            save_actress_to_server(item)
        if len(result['actress'])<hits:
            break
        offset += hits
def getActressById(actress_id):
    dmm = DMMAPI(api_id, affiliate_id)
    result = dmm.getActressSearch(actress_id=actress_id)['result']
    for item in result['actress']:
        save_actress_to_server(item)

def save_actress_to_server(item):
    fanza_id = item['id']
    name = item['name']
    if name=='このIDは使われておりません':
        return
    # ruby = item['ruby']
    bust = item.get('bust',None)
    cup = item.get('cup',None)
    waist = item.get('waist',None)
    hip = item.get('hip',None)
    height = item.get('height',None)
    birthday = item.get('birthday',None)
    blood_type = item.get('blood_type',None)
    hobby = item.get('blood_type',None)
    if hobby and len(hobby)==0:
        hobby = None
    prefectures = item.get('prefectures',None)
    if prefectures and len(prefectures)==0:
        prefectures = None
    avatar = None
    piccode = None
    if 'imageURL' in item:
        if 'large' in item['imageURL']:
            avatar = item['imageURL']['large']
            piccode = re.findall('actjpgs/(.*?)\.jpg', avatar)[0]
        elif 'small' in item['imageURL']:
            avatar = item['imageURL']['small']
            piccode = re.findall('thumbnail/(.*?)\.jpg', avatar)[0]
    if piccode=='printing':
        avatar=None
        piccode=None
    elif avatar:
        img = CrawlerHelper.get_requests(avatar, is_stream=True)
        if img is None or "printing" in img.url:
            avatar = None
            piccode = None
    DBHelper.save_actress(actname=name, act_fanzaid=fanza_id, birthday=birthday, height=height,
                          bloodtype=blood_type, cup=cup, bust=bust, waist=waist, hips=hip,
                          birthplace=prefectures, hobby=hobby, piccode=piccode, avatar=avatar)

def save_videoa_to_server(item):
    actresslist = []
    actress_fanzaidlist = {}
    for actress in item['iteminfo'].get('actress', []):
        actresslist.append(actress['name'])
        actress_fanzaidlist[actress['id']] = actress['name']
        if not DBHelper.get_actress_by_fanza_id(actress['id']):
            getActressById(actress['id'])
    genrelist = [genre['name'] for genre in item['iteminfo'].get('genre', [])]
    piccount = len(item['sampleImageURL']['sample_s']['image']) if 'sampleImageURL' in item else 0

    avobj = DBHelper.get_movie_by_cid(1, item['content_id'])
    if avobj:
        if avobj.piccount < piccount:
            avobj.piccount = piccount
            DBHelper.session.commit()
        if avobj.actresses.count() >= len(actresslist):
            return
    if 'maker' in item['iteminfo']:
        DBHelper.save_studio_fanzaid(item['iteminfo']['maker'][0]['name'], item['iteminfo']['maker'][0]['id'])

    DBHelper.save_movie(code=Tools.get_dvdid(item['content_id'], item['product_id'], 1),
                        cid=item['content_id'],
                        title=item['title'], length=item['volume'], rdate=item.get('date', None),
                        director=item['iteminfo']['director'][0]['name'] if 'director' in item[
                            'iteminfo'] else None,
                        studio=item['iteminfo']['maker'][0]['name'] if 'maker' in item['iteminfo'] else None,
                        label=item['iteminfo']['label'][0]['name'] if 'label' in item['iteminfo'] else None,
                        series=item['iteminfo']['series'][0]['name'] if 'series' in item['iteminfo'] else None,
                        piccode=item['product_id'],
                        piccount=piccount,
                        source=1,
                        actresslist=[], genrelist=genrelist, histrionlist=[],
                        actress_fanzaidlist=actress_fanzaidlist, histrion_fanzaidlist={})

def save_videoc_to_server(item):
    actresslist = []
    actress_fanzaidlist = {}
    for actress in item['iteminfo'].get('actress', []):
        actresslist.append(actress['name'])
        actress_fanzaidlist[actress['id']] = actress['name']
    genrelist = [genre['name'] for genre in item['iteminfo'].get('genre', [])]
    piccount = len(item['sampleImageURL']['sample_s']['image']) if 'sampleImageURL' in item else 0

    piccode = None
    if 'list' in item['imageURL']:
        piccode = re.findall(f'{item["content_id"]}/(.*?)jm\.', item['imageURL']['list'])[0]
    elif 'small' in item['imageURL']:
        piccode = re.findall(f'{item["content_id"]}/(.*?)jm\.', item['imageURL']['small'])[0]
    elif 'large' in item['imageURL']:
        piccode = re.findall(f'{item["content_id"]}/(.*?)jp\.', item['imageURL']['large'])[0]
    lengthstr = item.get('volume', None)
    if lengthstr:
        lenarr = lengthstr.split(':')
        length = 60 * int(lenarr[0]) + int(lenarr[1])
    else:
        length = None
    avobj = DBHelper.get_movie_by_cid(4, item['content_id'])
    if avobj:
        if avobj.piccount < piccount:
            avobj.piccount = piccount
            DBHelper.session.commit()
        if avobj.actresses.count() >= len(actresslist):
            return
    if 'maker' in item['iteminfo']:
        DBHelper.save_studio_fanzaid(item['iteminfo']['maker'][0]['name'], item['iteminfo']['maker'][0]['id'])
    DBHelper.save_movie(code=Tools.get_dvdid(item['content_id'], item['product_id'], 1),
                        cid=item['content_id'],
                        title=item['title'], length=length, rdate=item.get('date', None),
                        director=item['iteminfo']['director'][0]['name'] if 'director' in item['iteminfo'] else None,
                        studio=item['iteminfo']['maker'][0]['name'] if 'maker' in item['iteminfo'] else None,
                        label=item['iteminfo']['label'][0]['name'] if 'label' in item['iteminfo'] else None,
                        series=item['iteminfo']['series'][0]['name'] if 'series' in item['iteminfo'] else None,
                        piccode=piccode,
                        piccount=piccount,
                        source=4,
                        actresslist=[], genrelist=genrelist, histrionlist=[],
                        actress_fanzaidlist=actress_fanzaidlist, histrion_fanzaidlist={})

if __name__ == '__main__':
    #print(datetime.now().strftime('%Y-%m-%d T%H:%M:%S'))
    # getNewRealseDigitalVideoaItem()
    # getNewRealseDigitalVideocItem()
    # getNewRealseMonoDVDItem()
    dmm=DMMAPI(api_id,affiliate_id)
    # # print(dmm.getFloorList())
    #res=dmm.getItemList(service='mono',floor='dvd',hits=100,offset=1,lte_date='2022-06-01T00:00:00',sort='date')
    # res = dmm.getItemList(service='mono', floor='dvd', hits=100, offset=1, sort='date')
    # #res=dmm.getActressSearch(hits=100,sort='-id')
    # print(res)
    # res = dmm.getItemList(service='digital', floor='videoa', cid='41csv006', sort='date')
    res = dmm.getActressSearch(hits=100,offset=1,sort='-id',actress_id=1069384)
    print(res)
    # getAllActress()
