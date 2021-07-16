from model import *
import pictures
def getpv(av:AV):
    result=[]
    if av.source==1:
        pvcodelist=[av.piccode, av.piccode.replace('00','',1)]
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_dmb_w.mp4')
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_dm_w.mp4')
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_sm_w.mp4')
        for pvcode in pvcodelist:
            result.append(
                f'https://cc3001.dmm.co.jp/litevideo/freepv/{pvcode[0]}/{pvcode[0:3]}/{pvcode}/{pvcode}_sm_s.mp4')
        return result
    elif av.source==2:
        if av.studio.name == 'プレステージ':
            # 蚊香社
            result.append(f'https://www.prestige-av.com/sample_movie/{av.code}.mp4')
        if av.studio.name == 'MAXING':
            result.append(f'https://www.maxing.jp/dl/pc/{av.code}.mp4')
        #mgs预告 只能部分识别 且需翻墙
        result.append(
            f'https://sample.mgstage.com/sample/{pictures.get_mgscode(av.studio_id)}/{av.piccode.replace("-", "/").lower()}/{av.piccode}_sample.mp4')
        return result
    return None
