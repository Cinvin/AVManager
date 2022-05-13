import string

from model import *
import pictures
def getpv(av:AV):

    result=[]
    #studio
    if av.studio:
        if av.studio.name == 'プレステージ' or av.source == 1001:
            # 蚊香社
            result.append(f'https://www.prestige-av.com/sample_movie/{av.code}.mp4')
        elif av.studio.name == 'MAXING':
            result.append(f'https://www.maxing.jp/dl/pc/{av.code}.mp4')
        elif av.studio.name == 'ホットエンターテイメント':
            result.append(f'http://www.hot-et.com/item/movies/cm/{av.code}.mp4')
    #source
    if av.source in [1,3,4]:
        pvcodelist=[av.cid]
        if av.cid != av.piccode:
            if ' ' not in av.piccode:
                pvcodelist.append(av.piccode)
            else:
                strarr=av.piccode.split(' ')
                for s in strarr:
                    if s not in pvcodelist:
                        pvcodelist.append(s)

        vid=av.piccode.rstrip(string.digits)
        vid=av.piccode.replace(vid+'00',vid,1)
        if vid not in pvcodelist:
            pvcodelist.append(vid)
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_mhb_w.mp4')
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_dmb_w.mp4')
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_dm_w.mp4')
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_sm_w.mp4')
    elif av.source==2:
        #mgs
        if av.piccode:
            result.append(
                f'https://sample.mgstage.com/sample/{pictures.get_mgscode(av.studio_id)}/{av.cid.replace("-", "/").lower()}/{av.piccode}.mp4')
    elif av.source == 5 or av.source == 6:
        if '|' in av.piccode:
            result.append(
            f'https://ppvclips02.aventertainments.com/{av.piccode.split("|")[1]}')
    elif av.source == 1005:
        if av.piccode:
            result.append(
            f'https://smovie.1pondo.tv/sample/movies/{av.code}/{av.piccode}.mp4')
    elif av.source == 1006:
        if av.piccode:
            result.append(
            f'http://smovie.caribbeancom.com/sample/movies/{av.code}/{av.piccode}.mp4')
    elif av.source == 1007:
        if av.piccode:
            result.append(
            f'https://smovie.10musume.com/sample/movies/{av.code}/{av.piccode}.mp4')
    elif av.source == 1009:
        result.append(
            f'http://sample.heyzo.com/contents/3000/{av.code.split("-", 1)[1]}/heyzo_hd_{av.code.split("-", 1)[1]}_sample.mp4')
        result.append(
            f'http://sample.heyzo.com/contents/3000/{av.code.split("-", 1)[1]}/heyzo_lt_{av.code.split("-", 1)[1]}_sample.mp4')
        result.append(
            f'http://sample.heyzo.com/contents/3000/{av.code.split("-", 1)[1]}/heyzo_mb_{av.code.split("-", 1)[1]}_sample.mp4')
    elif av.source == 1010:
        result.append(
            f'https://my.cdn.tokyo-hot.com/media/samples/{av.cid}.mp4')

    return result if len(result)>0 else None
