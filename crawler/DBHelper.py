import re
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
from model import *
from sqlalchemy import create_engine, exists, func, and_, or_
from sqlalchemy.orm import sessionmaker
from difflib import SequenceMatcher

def get_session():
    engine = create_engine(sqlconnstr)
    DBsession = sessionmaker(bind=engine)
    session = DBsession()
    return session

session=get_session()

def check_dvdid_exist(code):
    avitem = session.query(AV).filter_by(code=code).first()
    return avitem
def check_cid_exist(cid):
    avitem = session.query(AV).filter_by(cid=cid).first()
    return avitem
def check_piccode_exist(piccode):
    avitem = session.query(AV).filter_by(piccode=piccode).first()
    return avitem

def check_title_exist_with_studio(title,studio=None,studio_id=None):
    if not studio and not studio_id:
        return None
    if not studio_id:
        studio_id = session.query(Studio).filter_by(name=studio).first()
        if studio_id:
            studio_id = studio_id.id
        else:
            return None

    avitem = session.query(AV).filter(and_(AV.title == title, AV.studio_id == studio_id)).first()
    return avitem

def check_dvdid_exist_with_studioid(code,studio=None,studio_id=None):
    if not studio and not studio_id:
        return None
    if not studio_id:
        studio_id = session.query(Studio).filter_by(name=studio).first()
        if studio_id:
            studio_id = studio_id.id
        else:
            return None
    avitem = session.query(AV).filter(and_(AV.code == code, AV.studio_id == studio_id)).first()
    return avitem

def check_movie_exist_with_title_similar(code,title):
    ignorechars='-|_|\*|●|・|･|【|】|～|’|…|。|！|\［|\］|\(|\)|（|）|「|『|』|」|!|？|\?| |\\|￥|　'
    t1 = re.sub(ignorechars, '', title)
    t1=t1.lower()
    l1=len(t1)
    avs = session.query(AV).filter(and_(AV.code == code, AV.source != 2)).all()
    for av in avs:
        t2 = re.sub(ignorechars, '', av.title)
        t2 = t2.lower()
        l2=len(t2)
        similar = SequenceMatcher(None, t1, t2).ratio()
        if similar>=0.5*min(l1,l2)/max(l1,l2):
            return True
    return False

def get_movie_obj(code,studio=None, studio_id=None):
    if not studio and not studio_id:
        return None
    if not studio_id:
        studio_id = session.query(Studio).filter_by(name=studio).first()
        if studio_id:
            studio_id = studio_id.id
        else:
            return None
    avitem = session.query(AV).filter_by(code=code, studio_id=studio_id).first()
    return avitem

def get_movie_by_cid(source,cid):
    avitem = session.query(AV).filter_by(source=source,cid=cid).first()
    return avitem

def save_movie(code, title, category=1, length=None, rdate=None, director=None, studio=None, label=None, series=None,
               piccode=None, piccount=0, cid=None,source:int=1,
               actresslist: list = [], genrelist: list = [],histrionlist: list = [] ,id=None):

    if not cid and source == 1:
        cid = piccode

    isnew = False

    avitem = None
    if id:
        avitem = session.query(AV).filter_by(id=id).first()
    elif cid:
        avitem = get_movie_by_cid(source, cid)
    else:
        avitem = get_movie_obj(code=code, studio=studio)

    if avitem is None:
        isnew=True
        avitem = AV()
        session.add(avitem)

    if code is None and isnew:
        code = '@' + cid
    if code is not None:
        avitem.code = code

    avitem.title = title
    if rdate is not None:
        avitem.rdate = rdate
    if isnew:
        avitem.category=category
    if length is not None:
        avitem.length = length
    if director is not None:
        directorobj = session.query(Director).filter_by(name=director).first()
        if directorobj is None:
            directorobj = Director()
            session.add(directorobj)
            directorobj.name = director
        avitem.director = directorobj

    if studio is not None:
        if category!=3:
            studioobj = session.query(Studio).filter_by(name=studio).first()
        else:
            studioobj = session.query(Studio).filter_by(name=studio,category=3).first()
        if studioobj is None:
            studioobj = Studio()
            session.add(studioobj)
            studioobj.name = studio
            if category==3:
                studioobj.category = 3
        avitem.studio = studioobj

    if label is not None:
        labelobj = session.query(Label).filter_by(name=label).first()
        if labelobj is None:
            labelobj = Label()
            session.add(labelobj)
            labelobj.name = label
        avitem.label = labelobj
    if series is not None:
        seriesobj = session.query(Series).filter_by(name=series).first()
        if seriesobj is None:
            seriesobj = Series()
            session.add(seriesobj)
            seriesobj.name = series
        avitem.series = seriesobj

    avitem.piccount = piccount
    avitem.piccode = piccode
    avitem.source = source

    avitem.cid=cid


    #if len(actresslist) > 0:
    actresses = session.query(Actress).filter(Actress.actname.in_(actresslist)).all()
    for actname in actresslist:
        if len(actname) > 64:
            continue
        found = False
        for act in actresses:
            if act.actname == actname:
                found = True
                break
        if not found:
            act = Actress()
            act.actname = actname
            actresses.append(act)
            session.add(act)
    avitem.actresses = actresses
    #if len(histrionlist) > 0:
    histrions = session.query(Histrion).filter(Histrion.actname.in_(histrionlist)).all()
    for actname in histrionlist:
        if len(actname) > 64:
            continue
        found = False
        for act in histrions:
            if act.actname == actname:
                found = True
                break
        if not found:
            act = Histrion()
            act.actname = actname
            histrions.append(act)
            session.add(act)
    avitem.histrions = histrions
    #if len(genrelist) > 0:
    genres = session.query(Genre).filter(Genre.name_ja.in_(genrelist)).all()
    for genrename in genrelist:
        found = False
        for gr in genres:
            if gr.name_ja == genrename:
                found = True
                break
        if not found:
            gr = Genre()
            gr.name = genrename
            gr.name_tw = genrename
            gr.name_ja = genrename
            genres.append(gr)
            session.add(gr)
    avitem.genres = genres
    printtext = f"[{datetime.now().strftime('%m-%d %H:%M:%S')}] {avitem.cid} {avitem.code} {avitem.title} {avitem.rdate}"
    session.commit()
    session.close()
    if isnew:
        printtext+=' new'
    else:
        printtext+=' update'
    print(printtext)

def save_movie_actress(cid,source,actresslist):
    avitem = get_movie_by_cid(source, cid)
    if not avitem:
        return
    actresses = session.query(Actress).filter(Actress.actname.in_(actresslist)).all()
    for actname in actresslist:
        if len(actname) > 64:
            continue
        found = False
        for act in actresses:
            if act.actname == actname:
                found = True
                break
        if not found:
            act = Actress()
            act.actname = actname
            actresses.append(act)
            session.add(act)
    avitem.actresses = actresses
    session.commit()

def save_mgscode(studio,mgscode):
    studioobj = session.query(Studio).filter_by(name=studio).first()
    if studioobj is None:
        studioobj = Studio()
        session.add(studioobj)
        studioobj.name = studio
    studioobj.mgscode=mgscode
    session.commit()

def save_actress_fanzaid(actname,fanzaid):
    actressobj = session.query(Actress).filter_by(actname=actname).first()
    if actressobj is None:
        actressobj = Actress()
        session.add(actressobj)
        actressobj.actname = actname
    actressobj.fanzaid = fanzaid
    session.commit()

def get_actname_by_fanzaid(fanzaid):
    actressobj = session.query(Actress).filter_by(fanzaid=fanzaid).first()
    if actressobj:
        return actressobj.actname
    return None

def save_actress_mainid(actname,mainid):
    actressobj = session.query(Actress).filter_by(actname=actname).first()
    if actressobj is None:
        actressobj = Actress()
        session.add(actressobj)
        actressobj.actname = actname
    actressobj.mainid = mainid
    session.commit()

def save_histrion_fanzaid(actname,fanzaid):
    histrionobj = session.query(Histrion).filter_by(actname=actname).first()
    if histrionobj is None:
        histrionobj = Histrion()
        session.add(histrionobj)
        histrionobj.actname = actname
    histrionobj.fanzaid = fanzaid
    session.commit()

def save_studio_fanzaid(studio,fanzaid):
    studioobj = session.query(Studio).filter_by(name=studio).first()
    if studioobj is None:
        studioobj = Studio()
        session.add(studioobj)
        studioobj.name = studio
    studioobj.fanzaid=fanzaid
    session.commit()

def delete_movie(id):
    movie=session.query(AV).filter(AV.id == id).first()
    if not movie:
        return
    session.delete(movie)
    session.commit()
    session.close()
