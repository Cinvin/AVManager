import requests
from flask import request
from flask import render_template, redirect, url_for, jsonify
from sqlalchemy import func, exists, and_, or_

from face.predict import predictimage, draw_prediction_labels_on_image
from model import *
import datetime
import base64
import pictures
import promo
from stats import geteecharts


@app.route('/', methods=["GET", "POST"])
@app.route('/page/<int:page_index>', methods=["GET", "POST"])
@app.route('/<filtertype>/', methods=["GET", "POST"])
@app.route('/<filtertype>/page/<int:page_index>', methods=["GET", "POST"])
@app.route('/<filtertype>/<filterkey>', methods=["GET", "POST"])
@app.route('/<filtertype>/<filterkey>/page/<int:page_index>', methods=["GET", "POST"])
def movielist(filtertype=None, filterkey=None, page_index=1):
    if filtertype is None:
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "search":
        filterkey = filterkey.strip()
        resultquery = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter(1 == 2)
        # 搜女优名字
        acts = Actress.query.filter_by(actname=filterkey).all()
        if len(acts) == 1:
            return redirect(url_for('movielist', filtertype='actress', filterkey=acts[0].id))
        acts = Actress.query.filter(Actress.actname.like(f"%{filterkey}%")).all()
        for act in acts:
            actquery = act.avs.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source)
            resultquery = resultquery.union(actquery)

        # 搜番号
        codequery = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter_by(code=filterkey)
        codecount = codequery.count()
        if codecount == 1:
            return redirect(url_for('movie', id=codequery[0].id))
        elif codecount == 0:
            codequery = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter(
                AV.code.like(f"%{filterkey}%"))
        resultquery = resultquery.union(codequery)
        # 搜标题
        titlequery = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter(
            AV.title.like(f"%{filterkey}%"))
        resultquery = resultquery.union(titlequery)
        pagination = resultquery.order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "released":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
            .filter(db.func.date(AV.rdate) <= datetime.datetime.today()) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "random":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
            .order_by(func.rand()).from_self() \
            .limit(30).from_self() \
            .paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "director":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter_by(director_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "studio":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter_by(studio_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "label":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter_by(label_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "series":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source).filter_by(series_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "genre":
        genrequery = Genre.query.filter_by(id=filterkey).first()
        if genrequery is not None:
            pagination = genrequery.avs.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
                .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
        else:
            pagination = None

    elif filtertype == "actress":
        actressitem = Actress.query.filter_by(id=filterkey).first()
        pagination = actressitem.avs.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
        if page_index != 1:
            actressitem = None
        elif actressitem.birthday is not None:
            today = datetime.date.today()  # 现在的日期
            age = int(round((today - actressitem.birthday).days / 365, 7))
            actressitem.age = age
        pslist = None
        if pagination and pagination.items:
            pslist = pictures.get_pslist(pagination.items)
        return render_template('main.html', pagetype="movielist", actress=actressitem, pslist=pslist,
                               pagination=pagination, pagination_endpoint="movielist", pagination_vals={"filtertype":filtertype,"filterkey":filterkey})
    else:
        pagination = None
    pslist=None
    if pagination and pagination.items:
        pslist=pictures.get_pslist(pagination.items)
    return render_template('main.html', pagetype="movielist", pslist=pslist,
                           pagination=pagination, pagination_endpoint="movielist", pagination_vals={"filtertype":filtertype,"filterkey":filterkey})

#收藏
@app.route('/favorite/', methods=["POST"])
def favorite():
    ftype = request.form['ftype']
    fid = request.form['fid']
    val = request.form['val'] == "true"

    if ftype is None:
        return ""
    fv = Favorite.query.filter_by(ftype=ftype, fid=fid).first()
    from model import db
    if fv is None and val:
        fv = Favorite()
        fv.fid = fid
        fv.ftype = ftype
        db.session.add(fv)
        db.session.commit()
    elif not val and fv is not None:
        db.session.delete(fv)
        db.session.commit()

    return ""
#收藏夹
@app.route('/favorites/<ftype>', methods=["GET", "POST"])
@app.route('/favorites/<ftype>/page/<int:page_index>', methods=["GET", "POST"])
def favorites(ftype, page_index=1):
    if ftype=="all":
        resultquery = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
            .filter(or_(
            and_(AV.id == Favorite.fid, Favorite.ftype == 1),
            and_(AV.studio_id == Favorite.fid, Favorite.ftype == 3),
            and_(AV.label_id == Favorite.fid, Favorite.ftype == 4),
            and_(AV.series_id == Favorite.fid, Favorite.ftype == 5),
        ))
        acts = Actress.query.filter(Actress.id == Favorite.fid , Favorite.ftype == 2).all()

        for act in acts:
            actquery = act.avs.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source)
            resultquery = resultquery.union(actquery)
        pagination = resultquery.order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
        pslist = None
        if pagination and pagination.items:
            pslist = pictures.get_pslist(pagination.items)
        return render_template('main.html', pagetype="movielist", pslist=pslist,
                               pagination=pagination, pagination_endpoint="favorites",
                               pagination_vals={"ftype": ftype})
    elif ftype=="movie":
        pagination = AV.query.with_entities(AV.id, AV.code, AV.title, AV.rdate, AV.piccode, AV.studio_id, AV.source) \
            .filter(AV.id == Favorite.fid, Favorite.ftype == 1)\
            .paginate(page_index, per_page=30, error_out=False)
        pslist = None
        if pagination and pagination.items:
            pslist = pictures.get_pslist(pagination.items)
        return render_template('main.html', pagetype="movielist", pslist=pslist,
                               pagination=pagination, pagination_endpoint="favorites",
                               pagination_vals={"ftype": ftype})
    elif ftype=="actress":
        counts = func.count(1)
        pagination = Actress.query.with_entities(Actress.id, Actress.actname, Actress.piccode) \
            .join(av_actress) \
            .filter(Actress.id == Favorite.fid , Favorite.ftype == 2) \
            .order_by(counts.desc(), Actress.piccode) \
            .group_by(Actress.id) \
            .paginate(page_index, per_page=35, error_out=False)
        return render_template('main.html', pagetype="actresslist",
                               pagination=pagination, pagination_endpoint="favorites", pagination_vals={"ftype": ftype})
    elif ftype=="studio":
        pagination = Studio.query \
            .with_entities(Studio.id, Studio.name, func.count('*').label('count')) \
            .join(AV) \
            .filter(Studio.id == Favorite.fid, Favorite.ftype == 3) \
            .order_by(func.count('*').desc()) \
            .group_by(Studio.id) \
            .paginate(page_index, per_page=120, error_out=False)
        return render_template('main.html', tagtype="studio",
                               pagination=pagination, pagination_endpoint="favorites", pagination_vals={"ftype": ftype})
    elif ftype=="label":
        pagination = Label.query \
            .with_entities(Label.id, Label.name, func.count('*').label('count')) \
            .join(AV) \
            .filter(Label.id == Favorite.fid, Favorite.ftype == 4) \
            .order_by(func.count('*').desc()) \
            .group_by(Label.id) \
            .paginate(page_index, per_page=120, error_out=False)
        return render_template('main.html', tagtype="label",
                               pagination=pagination, pagination_endpoint="favorites", pagination_vals={"ftype": ftype})
    elif ftype=="series":
        pagination = Series.query \
            .with_entities(Series.id, Series.name, func.count('*').label('count')) \
            .join(AV) \
            .filter(Series.id == Favorite.fid, Favorite.ftype == 5) \
            .order_by(func.count('*').desc()) \
            .group_by(Series.id) \
            .paginate(page_index, per_page=120, error_out=False)
        return render_template('main.html', tagtype="series",
                               pagination=pagination, pagination_endpoint="favorites", pagination_vals={"ftype": ftype})
    return render_template('main.html', pagination=None, pagination_endpoint="favorites", pagination_vals={"ftype": ftype})

@app.route('/search/', methods=["GET", "POST"])
def searchmovielist():
    keyword = request.args.get('keyword', None)
    if keyword is None:
        return redirect(url_for('movielist'))
    return redirect(url_for('movielist', filtertype="search", filterkey=keyword))


@app.route('/actresses/', methods=["GET", "POST"])
def actresslist():
    page_index = request.args.get('page_index', 1)
    page_index = int(page_index)
    counts = func.count(1)
    pagination = Actress.query.with_entities(Actress.id, Actress.actname, Actress.piccode) \
        .join(av_actress) \
        .order_by(counts.desc(),Actress.piccode) \
        .group_by(Actress.id) \
        .paginate(page_index, per_page=35, error_out=False)
    return render_template('main.html', pagetype="actresslist",
                           pagination=pagination, pagination_endpoint="actresslist", pagination_vals={})


@app.route('/genre/')
@app.route('/genre/page/<int:page_index>', methods=["GET", "POST"])
def genrelist(page_index=1):
    pagination = Genre.query\
        .with_entities(Genre.id, Genre.name,func.count('*').label('count')) \
        .join(av_genre) \
        .order_by(func.count('*').desc()) \
        .group_by(Genre.id)\
        .paginate(page_index, per_page=120, error_out=False)
    return render_template('main.html', tagtype="genre",
                           pagination=pagination, pagination_endpoint="genrelist", pagination_vals={})

@app.route('/serises/')
@app.route('/serises/page/<int:page_index>', methods=["GET", "POST"])
def seriseslist(page_index=1):
    pagination = Series\
        .query.with_entities(Series.id, Series.name,func.count('*').label('count')) \
        .join(AV) \
        .order_by(func.count('*').desc()) \
        .group_by(Series.id)\
        .paginate(page_index, per_page=120, error_out=False)
    return render_template('main.html', tagtype="series",
                           pagination=pagination, pagination_endpoint="seriseslist", pagination_vals={})

# 详情页
@app.route('/movie/<int:id>')
def movie(id):
    movie = AV.query.filter_by(id=id).first()

    return render_template('main.html', pagetype="movie", movie=movie,
                           pictures=pictures.Pictures(movie),
                           promo=promo.getpv(movie))


@app.route('/stats/')
def stats():
    return render_template('main.html', pagetype="stats", echarts=geteecharts())


@app.route('/predict/')
def predict():
    return render_template('main.html', pagetype="predict")


@app.route('/predict_image/', methods=["POST"])
def predict_image():
    img = request.files.get('file', None)
    if img is None:
        return jsonify({"success": 404, "img": "", "html": "上传图片失败"})
    img = img.read()

    names, locations = predictimage(img)

    if len(names) == 0:
        base64_data = base64.b64encode(img)
        s = base64_data.decode()
        imgsrc = f'data:image/jpeg;base64,{s}'
        return jsonify({"success": 404, "img": imgsrc, "html": "未识别出人脸"})

    stats = Actress.query.with_entities(Actress.id, Actress.actname, Actress.piccode) \
        .filter(Actress.piccode.in_(names)).all()
    for stat in stats:
        while stat.piccode in names:
            names[names.index(stat.piccode)] = stat.actname

    result_image = draw_prediction_labels_on_image(img, zip(names, locations))
    base64_data = base64.b64encode(result_image)
    s = base64_data.decode()
    imgsrc = f'data:image/jpeg;base64,{s}'

    return jsonify({"success": 200, "img": imgsrc, "html": get_actressbox_html(stats)})


def get_actressbox_html(stats):
    basehtml = ""
    for actress in stats:
        basehtml += f"""<div class="item">
                <a class="avatar-box text-center" href="{url_for('movielist', filtertype='actress', filterkey=actress.id)}">
                    <div class="photo-frame">
"""
        if actress.piccode:
            basehtml += f"<img src='https://pics.dmm.co.jp/mono/actjpgs/{actress.piccode}.jpg' title=''>"
        else:
            basehtml += f"https://pics.dmm.co.jp/mono/actjpgs/nowprinting.gif' title=''>"
        basehtml += f"""
                    </div>
                    <div class="photo-info">
                        <span>{actress.actname}</span>
                    </div>
                </a>
            </div>"""
    return basehtml


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
