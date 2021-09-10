import os
import string
from sqlalchemy import func

from crawler import DBHelper
from model import *

cache1={}
cache2={}
def get_dvdid(cid,piccode,source):
    if source == 1:
        if '-' in piccode:
            return None
        if '_' in piccode.replace('h_','',1):
            return None
        if  piccode.startswith('pkc0'):
            return piccode.upper()
        if piccode.startswith('td0'):
            return None
        if piccode.startswith('165cd'):
            return None
        if piccode.startswith('55t') :
            return piccode[2:].upper().replace('00', '-', 1)
        if piccode.startswith('66cav'):
            return None
        if piccode.startswith('card000'):
            return None
        tempiccode=piccode
        if tempiccode.endswith('re01'):
            tempiccode=tempiccode[0:-4]

        suffixletter = ''
        while tempiccode[-1] in string.ascii_letters:
            suffixletter = tempiccode[-1] + suffixletter
            tempiccode = tempiccode[0:-1]

        numstr=tempiccode.replace(tempiccode.rstrip(string.digits),'',1)
        if len(numstr) == 0:
            return None
        numint=int(numstr)


        if numint>=10 and numint<=99:
            floornum=10
        elif numint>=100 and numint<=999:
            floornum = 100
        elif numint>=1000 and numint<=9999:
            floornum = 1000
        elif numint>=10000 and numint<=99999:
            floornum = 10000
        elif numint>=100000 and numint<=999999:
            floornum = 100000
        else:
            floornum = 0
        ft = "{0:0" + str(len(numstr)) + "d}"
        floorstr = ft.format(floornum)
        key1=f'{tempiccode.rstrip(string.digits)}{floorstr}'
        codehistoy=None
        if key1 in cache1:
            codehistoy=cache1[key1]
        else:
            av=DBHelper.session.query(AV)\
                .filter(and_(AV.source == 1,
                             AV.piccode != AV.code,
                             AV.piccode != tempiccode,
                             AV.piccode >= f'{tempiccode.rstrip(string.digits)}{floorstr}',
                             AV.piccode < f'{tempiccode.rstrip(string.digits)}999999999',
                             AV.piccode.like(f'{tempiccode.rstrip(string.digits)}%')))\
                .order_by(AV.piccode).first()
            if av:
                cache1[key1]=av.code
                codehistoy = cache1[key1]
        if not codehistoy:
            if tempiccode.rstrip(string.digits) in cache2:
                codehistoy = cache2[tempiccode.rstrip(string.digits)]
            else:
                av = DBHelper.session.query(AV) \
                    .filter(and_(AV.source == 1,
                                 AV.code.notlike('%@%'),
                                 func.char_length(AV.piccode) == len(piccode),
                                 AV.piccode != tempiccode,
                                 AV.piccode < f'{tempiccode.rstrip(string.digits)}999999999',
                                 AV.piccode.like(f'{tempiccode.rstrip(string.digits)}%'))) \
                    .order_by(AV.piccode).first()
                if av:
                    cache2[tempiccode.rstrip(string.digits)]=av.code
                    codehistoy = cache2[tempiccode.rstrip(string.digits)]
        if codehistoy:
            suffixletterhistoy = ''
            while codehistoy[-1] in string.ascii_letters:
                suffixletterhistoy = codehistoy[-1] + suffixletterhistoy
                codehistoy = codehistoy[0:-1]
            splitedlist=codehistoy.split('-')
            if len(splitedlist)>2:
                return None
            elif len(splitedlist)==1:
                if len(suffixletter)>0:
                    suffixletter=suffixletter.upper()
                    if len(suffixletterhistoy)>0 and suffixletterhistoy[0] in string.ascii_lowercase:
                        suffixletter=suffixletter.lower()
                numstr = tempiccode.replace(tempiccode.rstrip(string.digits),'').strip(string.ascii_letters)
                if len(numstr)==0:
                    return None
                prefix=codehistoy.rstrip(string.digits)
                numstrhistoy=codehistoy.replace(prefix,'',1)
                numlen=len(numstrhistoy)
                while len(numstr)>numlen:
                    numstr=numstr[1:]
                formater = "{0:0" + str(numlen) + "d}"
                return prefix+formater.format(int(numstr))+suffixletter
            else:
                if len(suffixletter) > 0:
                    suffixletter = suffixletter.upper()
                    if len(suffixletterhistoy) > 0 and suffixletterhistoy[0] in string.ascii_lowercase:
                        suffixletter = suffixletter.lower()
                prefix = splitedlist[0] + '-'
                while len(splitedlist[1])>0 and splitedlist[1][0] in string.ascii_letters:
                    prefix = prefix+splitedlist[1][0]
                    splitedlist[1]=splitedlist[1][1:]
                numstr = tempiccode.replace(tempiccode.rstrip(string.digits),'')
                numlen = len(splitedlist[1])
                while len(numstr)>numlen:
                    numstr=numstr[1:]
                formater = "{0:0" + str(numlen) + "d}"
                return prefix + formater.format(int(numstr)) + suffixletter
        if tempiccode.startswith('h_'):
            tempiccode = tempiccode.replace('h_', '', 1)
        tempiccode = tempiccode.lstrip(string.digits)
        prefix = tempiccode.rstrip(string.digits)

        if tempiccode.startswith('r18'):
            prefix = 'r18'
        elif tempiccode.startswith('u18'):
            prefix = 'u18'
        elif tempiccode.startswith('u30'):
            prefix = 'u30'
        else:
            prefix = prefix.lstrip(string.digits)
        numstr = tempiccode.replace(prefix, '', 1)
        if numstr.startswith('000') and len(numstr)==6:
            numstr=numstr[2:]
        elif numstr.startswith('00') and len(numstr)==5:
            numstr=numstr[2:]
        elif numstr.startswith('0') and len(numstr)==4:
            numstr = numstr[1:]

        return prefix.upper() + '-' + numstr + suffixletter.upper()
    elif source ==3:
        if cid.startswith('55') and len(cid)>=9 and cid[4:6] == 'id':
            return cid[2:6].upper() + '-' + cid[6:]
        elif cid.startswith('55t'):
            return cid[2:5].upper() + '-' + cid[5:]

        lremove=['gk','tk']
        for s in lremove:
            if cid.startswith(s):
                cid=cid.replace(s,'',1)
                break
        rremove = ['bod', 'dod','r','tk','tk2']
        for s in rremove:
            if cid.endswith(s):
                cid = cid[0:-len(s)]
        suffixletter=''
        while cid[-1] in string.ascii_letters:
            suffixletter=cid[-1]+suffixletter
            cid=cid[0:-1]
        if cid.startswith('h_'):
            cid = cid.replace('h_', '', 1)
        elif cid.startswith('n_'):
            cid = cid.replace('n_', '', 1)
        cid = cid.lstrip(string.digits)
        prefix=cid.rstrip(string.digits)
        numstr=cid.replace(prefix,'',1)
        numstr="{0:03d}".format(int(numstr))
        return prefix.upper()+'-'+numstr+suffixletter.upper()
    elif source == 2:
        if len(cid) <= 3:
            return cid
        is_makerstart = True
        for i in range(0, 3):
            if cid[i] not in string.digits:
                is_makerstart = False
                break
        if is_makerstart:
            return cid[3:]
        return cid
    return None

def show_notification(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

def dmm_title_transform(title):
    title=title.replace('★配信限定特典付★','')
    return title.strip()

if __name__ == '__main__':
    print(get_dvdid('42vr00136','42vr00136',1))
