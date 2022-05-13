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