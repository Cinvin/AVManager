import string
from datetime import datetime
import sys
sys.path.append("..")
from model import *
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

engine = create_engine(sqlconnstr)
DBsession = sessionmaker(bind=engine)
session = DBsession()

def check_dvdid_exist(code):
    avitem = session.query(AV).filter_by(code=code).first()
    return avitem

def check_movie_exist_with_title(code,title):
    avitem = session.query(AV).filter(AV.code == code and AV.title.like(f"%{title}%")).first()
    return avitem

def get_movie_obj(code,studio)->AV:
    studio_id = session.query(Studio).filter_by(name=studio).first()
    if studio_id:
        studio_id = studio_id.id
    avitem = session.query(AV).filter_by(code=code, studio_id=studio_id).first()
    return avitem

def save_movie(code, title, length, rdate=None, director=None, studio=None, label=None, series=None,
               piccode=None, piccount=None, source:int=1,
               actslist: list = [], genrelist: list = []):
    avitem = get_movie_obj(studio,code)
    if avitem is None:
        avitem = AV()
        session.add(avitem)

    avitem.code = code
    avitem.title = title
    if rdate is not None:
        avitem.rdate = rdate
    avitem.length = length
    if director is not None:
        directorobj = session.query(Director).filter_by(name=director).first()
        if directorobj is None:
            directorobj = Director()
            directorobj.name = director
        avitem.director = directorobj

    if studio is not None:
        studioobj = session.query(Studio).filter_by(name=studio).first()
        if studioobj is None:
            studioobj = Studio()
            studioobj.name = studio
        avitem.studio = studioobj

    if label is not None:
        labelobj = session.query(Label).filter_by(name=label).first()
        if labelobj is None:
            labelobj = Label()
            labelobj.name = label
        avitem.label = labelobj
    if series is not None:
        seriesobj = session.query(Series).filter_by(name=series).first()
        if seriesobj is None:
            seriesobj = Series()
            seriesobj.name = series
        avitem.series = seriesobj

    avitem.piccount = piccount
    avitem.piccode = piccode
    avitem.source = source

    if len(actslist) > 0:
        actresses = session.query(Actress).filter(Actress.actname.in_(actslist)).all()
        for actname in actslist:
            if len(actname)>50:
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
    if len(genrelist) > 0:
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
    session.commit()
    print(f"[{datetime.now().strftime('%m-%d %H:%M:%S')}] {code} {title} {rdate}")

def save_mgscode(studio,mgscode):
    studioobj = session.query(Studio).filter_by(name=studio).first()
    if studioobj is None:
        studioobj = Studio()
        studioobj.name = studio
    if studioobj.mgscode!=mgscode:
        studioobj.mgscode=mgscode
        session.commit()

def change_to_mgs_pic(piccode,studio):
    avitem = get_movie_obj(studio, piccode.lstrip(string.digits))
    if avitem:
        avitem.source=2
        avitem.piccode=piccode
        session.commit()

def get_video_obj_by_code(code:str):
    vitem = session.query(Video).filter(Video.code == code).first()
    return vitem
def save_videourl(code,url):
    vd=get_video_obj_by_code(code)
    if vd is None:
        vd=Video()
        vd.code=code
        session.add(vd)
    vd.url=url
    session.commit()