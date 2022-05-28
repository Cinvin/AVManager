import re
import string
from datetime import datetime,timedelta

import requests
import json

import model
import sqlhelper
from crawler import DBHelper, Tools, CrawlerHelper
import time
from crawler.shop.dmmapi import DMMAPI
api_id='ezuc1BvgM0f74KV4ZMmS'
affiliate_id='sakuradite-999'

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
    datelimit -= timedelta(days=45)
    gte_date = datelimit.strftime('%Y-%m-%d') + 'T00:00:00'
    while True:
        print(f'offset:{offset}')
        result = dmm.getItemList(service='mono', floor='dvd', hits=hits, offset=offset, lte_date=lte_date,gte_date=gte_date, sort='date')['result']
        total_count = result.get('total_count',0)
        items = result['items']
        for item in items:
            save_dvd_to_server(item)
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

def save_dvd_to_server(item):
    if 'volume' not in item or 'maker' not in item['iteminfo'] or 'maker_product' not in item or 'jancode' not in item:
        return
    code = item['maker_product']
    cid = item['content_id']
    title = item['title']
    studio = item['iteminfo']['maker'][0]['name']

    if 'genre' in item['iteminfo']:
        # 排除蓝光,出口，活动，DOD商品,ディスクオンデマンド
        exceptList = [6104, 6147, 6997, 6993, 6992, 6991, 6147,6561,6797,300019]
        for genreItem in item['iteminfo']['genre']:
            if genreItem['id'] in exceptList:
                return

    queryobj = DBHelper.check_cid_exist(cid)
    if not queryobj:
        queryobj = DBHelper.check_cid_exist(
            cid.replace(cid.rstrip(string.digits), cid.rstrip(string.digits) + '00', 1))
    if queryobj:
        if queryobj.code != code and queryobj.title == item['title']:
            queryobj.code = code
            DBHelper.session.commit()
        return
    if DBHelper.check_dvdid_exist_with_studioid(code, studio=studio, studio_id=None):
        return
    if DBHelper.check_movie_exist_with_title_similar(code, item['title']):
        return
    titleav = DBHelper.check_title_exist_with_studio(title, studio=studio)
    if titleav:
        if titleav.source != 3:
            return
    piccount = len(item['sampleImageURL']['sample_s']['image']) if 'sampleImageURL' in item else 0
    piccode = cid
    if piccount > 0:
        sampleurl = item['sampleImageURL']['sample_s']['image'][0]
        samplepiccode = re.findall('https://pics.dmm.co.jp/digital/video/(.*?)/', sampleurl)[0]
        if samplepiccode != piccode:
            piccode = piccode + ' ' + samplepiccode
            piccodeav = DBHelper.check_piccode_exist(samplepiccode)
            if piccodeav:
                return
    actresslist = []
    actress_fanzaidlist = {}
    for actress in item['iteminfo'].get('actress', []):
        actresslist.append(actress['name'])
        actress_fanzaidlist[actress['id']] = actress['name']
    genrelist = [genre['name'] for genre in item['iteminfo'].get('genre', [])]

    avobj = DBHelper.get_movie_by_cid(3, item['content_id'])
    if avobj:
        if avobj.piccount < piccount:
            avobj.piccount = piccount
            avobj.piccode = piccode
            DBHelper.session.commit()
        if avobj.code != code:
            avobj.code = code
            DBHelper.session.commit()
        if avobj.actresses.count() >= len(actresslist):
            return
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
    getNewRealseMonoDVDItem()
    # getNewRealseDigitalVideocItem()
    # getNewRealseDigitalVideoaItem()
