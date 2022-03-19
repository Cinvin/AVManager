import datetime
import functools
from model import *

class Pictures:
    def __init__(self,movie:AV):
        if movie.source==1:
            #backup:http://media.javmovie.com/thumb/avm200013pl.jpg
            #backup:https://jp.netcdn.space/digital/video/dsd00832/dsd00832-1.jpg
            self.poster_small = f'https://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}ps.jpg'
            self.poster_large = f'https://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}pl.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1+movie.piccount):
                self.detail_small.append(f'https://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}-{str(i)}.jpg')
                self.detail_large.append(f'https://pics.dmm.co.jp/digital/video/{movie.piccode}/{movie.piccode}jp-{str(i)}.jpg')
        elif movie.source==2:
            piccode=movie.cid.lower()
            makercode=get_mgscode(movie.studio_id)
            part1=piccode.replace('-', '/')
            # https://image.mgstage.com/images/documentv/277dcv/185/pf_o2_277dcv-185.jpg
            self.poster_small = f'https://image.mgstage.com/images/{makercode}/{part1}/pf_o1_{piccode}.jpg'
            #https://image.mgstage.com/images/prestigepremium/300maan/640/pb_e_300maan-640.jpg
            self.poster_large = f'https://image.mgstage.com/images/{makercode}/{part1}/pb_e_{piccode}.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(0, movie.piccount):
                #https://image.mgstage.com/images/prestigepremium/300maan/640/cap_t1_24_300maan-640.jpg
                self.detail_small.append(f'https://image.mgstage.com/images/{makercode}/{part1}/cap_t1_{str(i)}_{piccode}.jpg')
                #https://image.mgstage.com/images/prestigepremium/300maan/640/cap_e_24_300maan-640.jpg
                self.detail_large.append(f'https://image.mgstage.com/images/{makercode}/{part1}/cap_e_{str(i)}_{piccode}.jpg')
        elif movie.source == 3:
            #dmm dvd
            poster=movie.piccode
            sample=movie.piccode
            strarr=movie.piccode.split(' ')
            if len(strarr)>1:
                poster=strarr[0]
                sample=strarr[1]
            self.poster_small = f'https://pics.dmm.co.jp/mono/movie/adult/{poster}/{poster}ps.jpg'
            self.poster_large = f'https://pics.dmm.co.jp/mono/movie/adult/{poster}/{poster}pl.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1 + movie.piccount):
                self.detail_small.append(
                    f'https://pics.dmm.co.jp/digital/video/{sample}/{sample}-{str(i)}.jpg')
                self.detail_large.append(
                    f'https://pics.dmm.co.jp/digital/video/{sample}/{sample}jp-{str(i)}.jpg')
        elif movie.source == 4:
            self.poster_small = f'https://pics.dmm.co.jp/digital/amateur/{movie.cid}/{movie.piccode}jm.jpg'
            self.poster_large = f'https://pics.dmm.co.jp/digital/amateur/{movie.cid}/{movie.piccode}jp.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1 + movie.piccount):
                self.detail_small.append(
                    f'https://pics.dmm.co.jp/digital/amateur/{movie.cid}/{movie.cid}js-{"{0:03d}".format(i)}.jpg')
                self.detail_large.append(
                    f'https://pics.dmm.co.jp/digital/amateur/{movie.cid}/{movie.cid}jp-{"{0:03d}".format(i)}.jpg')
        elif movie.source == 5:
            piccode = movie.piccode.split('|')[0]
            poster = piccode
            sample = piccode
            strarr = piccode.split(' ')
            if len(strarr) > 1:
                poster = strarr[0]
                sample = strarr[1]
            # https://imgs02.aventertainments.com/new/jacket_images/{poster}.jpg
            # https://imgs02.aventertainments.com/new/bigcover/dvd1ccdv-100.jpg
            if movie.rdate >= datetime.datetime(2014, 2, 1, 0, 0):
                self.poster_small = f'https://imgs02.aventertainments.com/new/jacket_images/{poster}.jpg'
                self.poster_large = f'https://imgs02.aventertainments.com/new/bigcover/{poster}.jpg'
            else:
                self.poster_small = f'https://imgs02.aventertainments.com/archive/jacket_images/{poster}.jpg'
                self.poster_large = f'https://imgs02.aventertainments.com/archive/bigcover/{poster}.jpg'
            self.detail_small = [f'https://imgs02.aventertainments.com/archive/screen_shot/{sample}.jpg']
            self.detail_large = [f'https://imgs02.aventertainments.com/archive/screen_shot/{sample}.jpg']
        elif movie.source == 6:
            piccode = movie.piccode.split('|')[0]
            poster = piccode
            sample = piccode
            strarr = piccode.split(' ')
            if len(strarr) > 1:
                poster = strarr[0]
                sample = strarr[1]
            self.poster_small = f'https://imgs02.aventertainments.com/vodimages/large/{poster}.jpg'
            self.poster_large = f'https://imgs02.aventertainments.com/vodimages/xlarge/{poster}.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1 + movie.piccount):
                self.detail_small.append(
                    f'https://imgs02.aventertainments.com/vodimages/screenshot/large/{sample}/{"{0:03d}".format(i)}.jpg')
                self.detail_large.append(
                    f'https://imgs02.aventertainments.com/vodimages/screenshot/large/{sample}/{"{0:03d}".format(i)}.jpg')
        elif movie.source == 7:
            strarr = movie.piccode.split(' ')
            self.poster_small = f'https://us.netcdn.space/storage/{strarr[0]}'
            self.poster_large = f'https://us.netcdn.space/storage/{strarr[1]}'
            self.detail_small = []
            self.detail_large = []
        elif movie.source == 10:
            picsplits = movie.piccode.split(' ')
            posterarr=picsplits[0].split(':')
            # https://contents-thumbnail2.fc2.com/w360/storage{splits[0]}.contents.fc2.com/file/{splits[1]}
            self.poster_small = f'https://contents-thumbnail2.fc2.com/w360/storage{posterarr[0]}.contents.fc2.com/file/{posterarr[1]}'
            self.poster_large = f'https://storage{posterarr[0]}.contents.fc2.com/file/{posterarr[1]}'
            self.detail_small = []
            self.detail_large = []
            if len(picsplits)>1:
                smpicsplits=picsplits[1].split(',')
                for smpic in smpicsplits:
                    posterarr=smpic.split(':')
                    self.detail_small.append(
                        f'https://contents-thumbnail2.fc2.com/w240/storage{posterarr[0]}.contents.fc2.com/file/{posterarr[1]}')
                    self.detail_large.append(
                        f'https://storage{posterarr[0]}.contents.fc2.com/file/{posterarr[1]}')
        elif movie.source==1001:
            #prestige
            makercode = get_mgscode(movie.studio_id).replace("shirouto","shiroutotv")
            piccode = movie.piccode.lower()
            part1 = piccode.replace('-', '/')
            # https://www.prestige-av.com/images/corner/goods/prestige/afs/056/pf_p_afs-056.jpg
            self.poster_small = f'https://www.prestige-av.com/images/corner/goods/{makercode}/{part1}/pf_p_{piccode}.jpg'
            # https://www.prestige-av.com/images/corner/goods/prestige/afs/056/pb_e_afs-056.jpg
            self.poster_large = f'https://www.prestige-av.com/images/corner/goods/{makercode}/{part1}/pb_e_{piccode}.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(0, movie.piccount):
                # https://www.prestige-av.com/images/corner/goods/prestige/afs/056/cap_t1_14_afs-056.jpg
                self.detail_small.append(
                    f'https://www.prestige-av.com/images/corner/goods/{makercode}/{part1}/cap_t1_{str(i)}_{piccode}.jpg')
                # https://image.mgstage.com/images/prestigepremium/300maan/640/cap_e_24_300maan-640.jpg
                self.detail_large.append(
                    f'https://www.prestige-av.com/images/corner/goods/{makercode}/{part1}/cap_e_{str(i)}_{piccode}.jpg')
        elif movie.source==1003:
            # moodyz
            piccode = movie.piccode
            # https://www.prestige-av.com/images/corner/goods/prestige/afs/056/pf_p_afs-056.jpg
            self.poster_small = f'https://www.moodyz.com/contents/works/{piccode}/{piccode}-ps.jpg'
            # https://www.prestige-av.com/images/corner/goods/prestige/afs/056/pb_e_afs-056.jpg
            self.poster_large = f'https://www.moodyz.com/contents/works/{piccode}/{piccode}-pl.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(0, movie.piccount):
                # https://www.moodyz.com/contents/works/miv005/miv005-10-s.jpg
                self.detail_small.append(
                    f'https://www.moodyz.com/contents/works/{piccode}/{piccode}-{str(i)}-s.jpg')
                # https://www.moodyz.com/contents/works/miv005/miv005-10.jpg
                self.detail_large.append(
                    f'https://www.moodyz.com/contents/works/{piccode}/{piccode}-{str(i)}.jpg')
        elif movie.source==1004:
            # km-produce
            piccode = movie.piccode
            self.poster_small = f'https://www.km-produce.com/img/title0/{piccode}.jpg'
            self.poster_large = f'https://www.km-produce.com/img/title1/{piccode}.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1 + movie.piccount):
                index="{0:02d}".format(i)
                #https://www.km-produce.com/img/still0/{piccode}/{index}.jpg
                self.detail_small.append(
                    f'https://www.km-produce.com/img/still0/{piccode}/{index}.jpg')
                self.detail_large.append(
                    f'https://www.km-produce.com/img/still1/{piccode}/{index}.jpg')
        elif movie.source==1005:
            #https://www.1pondo.tv/assets/sample/{movie.code}/thum_b.jpg real
            #https://us.netcdn.space/storage/1pondo
            self.poster_small=f'https://us.netcdn.space/storage/1pondo/assets/sample/{movie.code}/thum_b.jpg'
            self.poster_large = f'https://us.netcdn.space/storage/1pondo/assets/sample/{movie.code}/str.jpg'
            self.detail_small = []
            self.detail_large = []
        elif movie.source==1006:
            if movie.rdate >= datetime.datetime(2007, 2, 17, 0, 0):
                self.poster_small= f'https://www.caribbeancom.com/moviepages/{movie.code}/images/jacket.jpg'
            elif movie.rdate >= datetime.datetime(2005,2,3,0,0):
                self.poster_small= f'https://www.caribbeancom.com/moviepages/{movie.code}/images/today.jpg'
            else:
                self.poster_small = f'https://www.caribbeancom.com/moviepages/{movie.code}/images/l_l.jpg'
            self.poster_large = f'https://www.caribbeancom.com/moviepages/{movie.code}/images/l_l.jpg'
            self.detail_small = []
            self.detail_large = []
        elif movie.source==1007:
            # https://www.10musume.com/assets/sample/{movie.code}/str.jpg
            # https://us.netcdn.space/storage/10musume/
            #                   https://us.netcdn.space/storage/10musume/moviepages/082821_01/images/list1.jpg
            self.poster_small=f'https://us.netcdn.space/storage/10musume/moviepages/{movie.code}/images/list1.jpg'
            #                     https://us.netcdn.space/storage/10musume/moviepages/082821_01/images/str.jpg
            self.poster_large = f'https://us.netcdn.space/storage/10musume/moviepages/{movie.code}/images/str.jpg'
            self.detail_small = []
            self.detail_large = []
        elif movie.source==1008:
            self.poster_small=f'https://www.pacopacomama.com/assets/sample/{movie.code}/l_thum.jpg'
            self.poster_large = f'https://www.pacopacomama.com/moviepages/{movie.code}/images/l_hd.jpg'
            self.detail_small = []
            self.detail_large = []
        elif movie.source == 1009:
            picid=movie.code.split("-", 1)[1]
            self.poster_small = f'https://www.heyzo.com/contents/3000/{picid}/images/thumbnail.jpg'
            self.poster_large = f'https://www.heyzo.com/contents/3000/{picid}/images/player_thumbnail.jpg'
            self.detail_small = []
            self.detail_large = []
            for i in range(1, 1 + movie.piccount):
                index = "{0:02d}".format(i)
                # https://www.heyzo.com/contents/3000/{picid}/gallery/thumbnail_001.jpg
                # https://www.heyzo.com/contents/3000/{picid}/gallery/001.jpg
                self.detail_small.append(
                    f'https://www.heyzo.com/contents/3000/{picid}/gallery/thumbnail_{"{0:03d}".format(i)}.jpg')
                self.detail_large.append(
                    f'https://www.heyzo.com/contents/3000/{picid}/gallery/{"{0:03d}".format(i)}.jpg')
        elif movie.source == 1010:
            #220x124
            self.poster_small = f'https://my.cdn.tokyo-hot.com/media/{movie.cid}/list_image/{movie.piccode}/220x124_default.jpg'
            self.poster_large = f'https://my.cdn.tokyo-hot.com/media/{movie.cid}/list_image/{movie.piccode}/820x462_default.jpg'
            self.detail_small = []
            self.detail_large = []

        elif movie.source == 1000:
            slpited=movie.piccode.split(' ')
            self.poster_small = slpited[0]
            self.poster_large = slpited[1]
            self.detail_small = []
            self.detail_large = []
def get_pslist(avs:list):
    pslist={}
    for av in avs:
        pslist[av.id]=get_psurl(av)
    return pslist
def get_psurl(av:AV):
    if av.source == 1:
        return f'http://pics.dmm.co.jp/digital/video/{av.piccode}/{av.piccode}ps.jpg'
    elif av.source == 2:
        piccode = av.cid.lower()
        part1 = piccode.replace('-', '/')
        # https://image.mgstage.com/images/documentv/277dcv/185/pf_o2_277dcv-185.jpg
        return f'https://image.mgstage.com/images/{get_mgscode(av.studio_id)}/{part1}/pf_o1_{piccode}.jpg'
    elif av.source == 3:
        piccode = av.piccode.split(' ')[0]
        return f'https://pics.dmm.co.jp/mono/movie/adult/{piccode}/{piccode}ps.jpg'
    elif av.source == 4:
        # https://pics.dmm.co.jp/digital/amateur/emst002/emst002jm.jpg
        return f'http://pics.dmm.co.jp/digital/amateur/{av.cid}/{av.piccode}jm.jpg'
    elif av.source == 5:
        piccode = av.piccode.split('|')[0].split(' ')[0]
        if av.rdate>=datetime.datetime(2014, 2, 1, 0, 0):
            #https://imgs02.aventertainments.com/new/jacket_images/dvd1lldv-100.jpg
            return f'https://imgs02.aventertainments.com/new/jacket_images/{piccode}.jpg'
        else:
            return f'https://imgs02.aventertainments.com/archive/jacket_images/{piccode}.jpg'
    elif av.source == 6:
        piccode = av.piccode.split('|')[0].split(' ')[0]
        #https://imgs02.aventertainments.com/archive/jacket_images/dvd1cwdv-26.jpg
        return f'https://imgs02.aventertainments.com/vodimages/large/{piccode}.jpg'
    elif av.source == 7:
        return f'https://us.netcdn.space/storage/{av.piccode.split(" ")[0]}'
    elif av.source == 10:
        picsplits = av.piccode.split(' ')
        posterarr = picsplits[0].split(':')
        #https://contents-thumbnail2.fc2.com/w360/storage{splits[0]}.contents.fc2.com/file/{splits[1]}
        return f'https://contents-thumbnail2.fc2.com/w360/storage{posterarr[0]}.contents.fc2.com/file/{posterarr[1]}'

    elif av.source == 1001:
        piccode = av.piccode.lower()
        part1 = piccode.replace('-', '/')
        # https://pics.dmm.co.jp/digital/amateur/emst002/emst002jm.jpg
        return f'https://www.prestige-av.com/images/corner/goods/{get_mgscode(av.studio_id).replace("shirouto","shiroutotv")}/{part1}/pf_p_{piccode}.jpg'
    elif av.source == 1003:
        piccode=av.piccode
        #https://www.moodyz.com/contents/works/mdi107/mdi107-ps.jpg
        return f'https://www.moodyz.com/contents/works/{piccode}/{piccode}-ps.jpg'
    elif av.source == 1004:
        piccode=av.piccode
        #https://www.km-produce.com/img/title0/vrkm-357.jpg
        return f'https://www.km-produce.com/img/title0/{piccode}.jpg'
    elif av.source == 1005:
        #https://www.1pondo.tv/assets/sample/{av.code}/thum_b.jpg real
        #https://us.netcdn.space/storage/1pondo
        return f'https://us.netcdn.space/storage/1pondo/assets/sample/{av.code}/thum_b.jpg'
    elif av.source == 1006:
        if av.rdate >= datetime.datetime(2014, 2, 1, 0, 0):
            return f'https://www.caribbeancom.com/moviepages/{av.code}/images/jacket.jpg'
        elif av.rdate >= datetime.datetime(2005, 2, 3, 0, 0):
            return f'https://www.caribbeancom.com/moviepages/{av.code}/images/today.jpg'
        else:
            return f'https://www.caribbeancom.com/moviepages/{av.code}/images/l_l.jpg'
    elif av.source == 1007:
        #https://www.10musume.com/moviepages/{av.code}/images/list1.jpg
        #https://us.netcdn.space/storage/10musume/
        #https://us.netcdn.space/storage/10musume/moviepages/081821_01/images/list1.jpg
        return f'https://us.netcdn.space/storage/10musume/moviepages/{av.code}/images/list1.jpg'
    elif av.source == 1008:
        return f'https://www.pacopacomama.com/assets/sample/{av.code}/l_thum.jpg'
    elif av.source == 1009:
        return f'https://www.heyzo.com/contents/3000/{av.code.split("-",1)[1]}/images/thumbnail.jpg'
    elif av.source == 1010:
        return f'https://my.cdn.tokyo-hot.com/media/{av.cid}/list_image/{av.piccode}/220x124_default.jpg'
    elif av.source == 1000:
        return av.piccode.split(' ')[0]

@functools.lru_cache()
def get_mgscode(studio_id):
    studio=Studio.query.with_entities(Studio.mgscode).filter_by(id=studio_id).first()
    if studio:
        return studio.mgscode
    return None