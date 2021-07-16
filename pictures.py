import functools
import re
from model import *

class Pictures:
    def __init__(self,movie:AV):
        if movie.source==1:
            #backup:https://jp.netcdn.space/digital/video/dsd00832/dsd00832-1.jpg
            self.poster_small = f'http://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}ps.jpg'
            self.poster_large = f'http://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}pl.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1+movie.piccount):
                self.detail_small.append(f'http://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}-{str(i)}.jpg')
                self.detail_large.append(f'http://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}jp-{str(i)}.jpg')
        elif movie.source==2:
            piccode=movie.piccode.lower()
            makercode=get_mgscode(movie.studio_id)
            part1=piccode.replace('-', '/')
            # https://image.mgstage.com/images/documentv/277dcv/185/pf_o2_277dcv-185.jpg
            self.poster_small = f'https://image.mgstage.com/images/{makercode}/{part1}/pf_o2_{piccode}.jpg'
            #https://image.mgstage.com/images/prestigepremium/300maan/640/pb_e_300maan-640.jpg
            self.poster_large = f'https://image.mgstage.com/images/{makercode}/{part1}/pb_e_{piccode}.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(0, movie.piccount):
                #https://image.mgstage.com/images/prestigepremium/300maan/640/cap_t1_24_300maan-640.jpg
                self.detail_small.append(f'https://image.mgstage.com/images/{makercode}/{part1}/cap_t1_{str(i)}_{piccode}.jpg')
                #https://image.mgstage.com/images/prestigepremium/300maan/640/cap_e_24_300maan-640.jpg
                self.detail_large.append(f'https://image.mgstage.com/images/{makercode}/{part1}/cap_e_{str(i)}_{piccode}.jpg')

def get_pslist(avs:list):
    pslist={}
    for av in avs:
        pslist[av.id]=get_psurl(av)
    return pslist
def get_psurl(av:AV):
    if av.source == 1:
        return f'http://pics.dmm.co.jp/digital/video/{av.piccode}/{av.piccode}ps.jpg'
    elif av.source == 2:
        piccode = av.piccode.lower()
        part1 = piccode.replace('-', '/')
        # https://image.mgstage.com/images/documentv/277dcv/185/pf_o2_277dcv-185.jpg
        return f'https://image.mgstage.com/images/{get_mgscode(av.studio_id)}/{part1}/pf_o2_{piccode}.jpg'

@functools.lru_cache()
def get_mgscode(studio_id):
    studio=Studio.query.with_entities(Studio.mgscode).filter_by(id=studio_id).first()
    if studio:
        return studio.mgscode
    return None