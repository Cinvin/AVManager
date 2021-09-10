from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlhelper import host, port ,user ,password ,dbname
from flask_cors import *

sqlconnstr = f"mysql+pymysql://{user}:{password}@{host}/{dbname}"

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.debug=True
app.config["SQLALCHEMY_DATABASE_URI"] = sqlconnstr
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# http://www.pythondoc.com/flask-sqlalchemy/config.html
db = SQLAlchemy(app)

av_genre = db.Table('t_av_genre',
         db.Column('id', db.Integer, primary_key=True,autoincrement=True),
         db.Column('genre', db.Integer, db.ForeignKey('t_genre.id',ondelete='CASCADE')),
         db.Column('av_id', db.Integer, db.ForeignKey('t_av.id',ondelete='CASCADE')),
         db.UniqueConstraint("av_id","genre",name="uq_av_genre")
         )
av_actress = db.Table('t_av_actress',
         db.Column('id', db.Integer, primary_key=True, autoincrement=True),
         db.Column('actress_id', db.Integer, db.ForeignKey('t_actress.id',ondelete='CASCADE')),
         db.Column('av_id', db.Integer, db.ForeignKey('t_av.id',ondelete='CASCADE')),
         db.UniqueConstraint("av_id","actress_id",name="uq_av_actress")
         )
av_histrion = db.Table('t_av_histrion',
         db.Column('id', db.Integer, primary_key=True, autoincrement=True),
         db.Column('histrion_id', db.Integer, db.ForeignKey('t_histrion.id',ondelete='CASCADE')),
         db.Column('av_id', db.Integer, db.ForeignKey('t_av.id',ondelete='CASCADE')),
         db.UniqueConstraint("av_id","histrion_id",name="uq_av_histrion")
         )

class AV(db.Model):
    __tablename__ = "t_av"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    category = db.Column(db.Integer)
    cid = db.Column(db.String(256), nullable=True)
    code = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    rdate = db.Column(db.Date)
    length = db.Column(db.Integer)
    piccode = db.Column(db.String(50), nullable=False)
    piccount = db.Column(db.Integer)
    source = db.Column(db.Integer)
    actresses = db.relationship('Actress', secondary=av_actress, backref=db.backref('avs', lazy='dynamic'), lazy='dynamic')
    histrions = db.relationship('Histrion', secondary=av_histrion, backref=db.backref('avs', lazy='dynamic'), lazy='dynamic')
    genres = db.relationship('Genre', secondary=av_genre, backref=db.backref('avs', lazy='dynamic'), lazy='dynamic')

    director_id = db.Column(db.Integer,db.ForeignKey('t_director.id'))
    label_id = db.Column(db.Integer, db.ForeignKey('t_label.id'))
    series_id = db.Column(db.Integer, db.ForeignKey('t_series.id'))
    studio_id = db.Column(db.Integer, db.ForeignKey('t_studio.id'))

    def is_favorite(self):
        favorite = Favorite.query \
            .filter(and_(Favorite.ftype == 1, Favorite.fid == self.id)).first()
        return favorite is not None


class Actress(db.Model):
    __tablename__="t_actress"
    id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    actname=db.Column(db.String(50),nullable=False)
    birthday=db.Column(db.Date)
    height = db.Column(db.Integer)
    cup = db.Column(db.String(50))
    bust = db.Column(db.Integer)
    waist = db.Column(db.Integer)
    hips = db.Column(db.Integer)
    birthplace = db.Column(db.String(255))
    hobby = db.Column(db.String(255))
    piccode = db.Column(db.String(50))
    mainid = db.Column(db.Integer)
    fanzaid = db.Column(db.Integer)

    def mainname(self):
        if self.mainid:
            return Actress.query \
                .filter(Actress.id == self.mainid).first().actname
        else:
            return None
    def subnames(self):
        qureyresult=Actress.query \
                .filter(Actress.mainid == self.id).all()
        if len(qureyresult)==0:
            return ''
        restext=''
        for act in qureyresult:
            restext=restext+act.actname+','
        restext=restext.strip(',')
        return f'({restext})'

    def is_favorite(self):
        favorite = Favorite.query \
            .filter(and_(Favorite.ftype == 2, Favorite.fid == self.id)).first()
        return favorite is not None


class Histrion(db.Model):
    __tablename__="t_histrion"
    id = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    actname = db.Column(db.String(50,collation='NOCASE'),nullable=False)
    fanzaid = db.Column(db.Integer)

class Director(db.Model):
    __tablename__ = "t_director"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50))
    avs = db.relationship('AV', backref='director', lazy=True)

class Genre(db.Model):
    __tablename__ = "t_genre"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50))
    name_tw = db.Column(db.String(50))
    name_ja = db.Column(db.String(50))
    name_en = db.Column(db.String(50))

class Label(db.Model):
    __tablename__ = "t_label"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(50))
    avs = db.relationship('AV', backref='label', lazy=True)
    def is_favorite(self):
        favorite = Favorite.query \
            .filter(and_(Favorite.ftype == 4, Favorite.fid == self.id)).first()
        return favorite is not None

class Series(db.Model):
    __tablename__ = "t_series"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    avs = db.relationship('AV', backref='series', lazy=True)
    def is_favorite(self):
        favorite = Favorite.query \
            .filter(and_(Favorite.ftype == 5, Favorite.fid == self.id)).first()
        return favorite is not None
class Studio(db.Model):
    __tablename__ = "t_studio"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    mgscode = db.Column(db.String(64), nullable=True)
    avs = db.relationship('AV', backref='studio', lazy=True)
    fanzaid = db.Column(db.Integer)

    category = db.Column(db.Integer)#3:FC2.Saler

    def is_favorite(self):
        favorite = Favorite.query \
            .filter(and_(Favorite.ftype == 3, Favorite.fid == self.id)).first()
        return favorite is not None

class Favorite(db.Model):
    __tablename__ = "t_favorite"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    fid = db.Column(db.Integer)
    ftype = db.Column(db.Integer)       # 1-movie 2-actress 3-studio 4-label 5-series