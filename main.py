import requests
from flask import request
from flask import render_template, redirect, url_for, jsonify
from sqlalchemy import func, exists, and_, or_
import numpy as np

from face.predict import predictimage, draw_prediction_labels_on_image
from model import *
import datetime
from pyecharts.charts import Line, Pie, Bar
from pyecharts import options as opts
import base64


@app.route('/', methods=["GET", "POST"])
@app.route('/page/<int:page_index>', methods=["GET", "POST"])
@app.route('/<filtertype>/', methods=["GET", "POST"])
@app.route('/<filtertype>/page/<int:page_index>', methods=["GET", "POST"])
@app.route('/<filtertype>/<filterkey>', methods=["GET", "POST"])
@app.route('/<filtertype>/<filterkey>/page/<int:page_index>', methods=["GET", "POST"])
def movielist(filtertype=None, filterkey=None, page_index=1):
    if filtertype is None:
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "search":
        filterkey = filterkey.strip()
        resultquery = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter(1 == 2)
        # 搜女优名字
        acts = Actress.query.filter_by(actname=filterkey).all()
        if len(acts) == 1:
            return redirect(url_for('movielist', filtertype='actress', filterkey=acts[0].id))
        acts = Actress.query.filter(Actress.actname.like(f"%{filterkey}%")).all()
        for act in acts:
            actquery = act.avs.with_entities(AV.code, AV.title, AV.rdate, AV.piccode)
            resultquery = resultquery.union(actquery)

        # 搜番号
        codequery = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter_by(code=filterkey)
        if codequery.count() == 1:
            return redirect(url_for('movie', cid=codequery[0].piccode))
        codequery = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter(
            AV.code.like(f"%{filterkey}%"))
        resultquery = resultquery.union(codequery)
        # 搜标题
        titlequery = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter(
            AV.title.like(f"%{filterkey}%"))
        resultquery = resultquery.union(titlequery)
        pagination = resultquery.order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "released":
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode) \
            .filter(db.func.date(AV.rdate) <= datetime.datetime.today()) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "random":
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode) \
            .order_by(func.rand()).from_self() \
            .limit(30).from_self() \
            .paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "director":
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter_by(director_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "studio":
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter_by(studio_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "label":
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter_by(label_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "series":
        pagination = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode).filter_by(series_id=filterkey) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "genre":
        genrequery = Genre.query.filter_by(id=filterkey).first().avs
        pagination = genrequery.with_entities(AV.code, AV.title, AV.rdate, AV.piccode) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
    elif filtertype == "favorite":
        resultquery = AV.query.with_entities(AV.code, AV.title, AV.rdate, AV.piccode) \
            .filter(or_(
            and_(AV.id == Favorite.fid, Favorite.ftype == 1),
            and_(AV.studio_id == Favorite.fid, Favorite.ftype == 3),
            and_(AV.label_id == Favorite.fid, Favorite.ftype == 4),
            and_(AV.series_id == Favorite.fid, Favorite.ftype == 5),
        ))
        acts = Actress.query.filter(exists().where(Actress.id == Favorite.fid and Favorite.ftype == 2)).all()

        for act in acts:
            actquery = act.avs.with_entities(AV.code, AV.title, AV.rdate, AV.piccode)
            resultquery = resultquery.union(actquery)

        pagination = resultquery.order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)

    elif filtertype == "actress":
        actressitem = Actress.query.filter_by(id=filterkey).first()
        pagination = actressitem.avs.with_entities(AV.code, AV.title, AV.rdate, AV.piccode) \
            .order_by(AV.rdate.desc(), AV.code).paginate(page_index, per_page=30, error_out=False)
        if page_index != 1:
            actressitem = None
        elif actressitem.birthday is not None:
            today = datetime.date.today()  # 现在的日期
            age = int(round((today - actressitem.birthday).days / 365, 7))
            actressitem.age = age
        return render_template('main.html', pagetype="movielist", pagination=pagination, filtertype=filtertype,
                               filterkey=filterkey, actress=actressitem)
    else:
        pagination = None
    return render_template('main.html', pagetype="movielist", pagination=pagination, filtertype=filtertype,
                           filterkey=filterkey)


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
    pagination = Actress.query.with_entities(Actress.id, Actress.actname, Actress.piccode) \
        .filter(Actress.avs.any()).paginate(page_index, per_page=30, error_out=False)
    return render_template('main.html', pagetype="actresslist", pagination=pagination)


@app.route('/genre/')
def genrelist():
    result = Genre.query.with_entities(Genre.id, Genre.name) \
        .join(av_genre) \
        .order_by(func.count('*').desc()) \
        .group_by(Genre.id).all()
    return render_template('main.html', pagetype="genrelist", genrelist=result)


# 详情页
@app.route('/movie/<string:cid>')
def movie(cid):
    movie = AV.query.filter_by(piccode=cid).first()
    return render_template('main.html', pagetype="movie", movie=movie)


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
        return jsonify({"success": 404, "img": "", "html": "未识别出人脸"})
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


@app.route('/proma/', methods=["GET", "POST"])
def get_promo():
    code = request.args.get('code', None)
    piccode = request.args.get('piccode', None)
    return get_promo_sub(code, piccode)


def get_promo_sub(code: str, piccode: str):
    baseurl = "https://cc3001.dmm.co.jp/litevideo/freepv/first/secord/third/third_dm_w.mp4"
    # backup https://awscc3001.r18.com/litevideo/freepv/j/jul/jul00474/jul00474_dmb_w.mp4
    mycode = code.lower()
    mycode = mycode.replace("-", "00")
    url = baseurl.replace("first", mycode[0])
    url = url.replace("secord", mycode[0:3])
    url = url.replace("third", mycode)

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        return mycode

    mycode = code.lower().replace("-", "")
    url = baseurl.replace("first", mycode[0])
    url = url.replace("secord", mycode[0:3])
    url = url.replace("third", mycode)

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        return mycode

    url = baseurl.replace("first", piccode[0])
    url = url.replace("secord", piccode[0:3])
    url = url.replace("third", piccode)

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        return piccode

    if "00" in piccode:
        mycode = piccode.replace("00", "")
        url = baseurl.replace("first", mycode[0])
        url = url.replace("secord", mycode[0:3])
        url = url.replace("third", mycode)

        r = requests.get(url, stream=True)
        if r.status_code == 200:
            return mycode
    return ""


def geteecharts():
    echarts = list()
    echarts.append(get_av_year_charts())
    echarts.append(get_cup_pie_charts())
    echarts.append(get_actress_height_charts())
    echarts.append(get_actress_num_rank())
    return echarts


def get_av_year_charts():
    years = func.date_format(AV.rdate, "%Y").label('year')
    result = AV.query.with_entities(years, func.count('*').label('year_count')) \
        .filter(AV.rdate.isnot(None)) \
        .order_by(years) \
        .group_by(years).all()
    a1, a2 = zip(*result)
    line = (
        Line(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', )
        )
            .add_xaxis(list(a1))
            .add_yaxis("数量", list(a2),
                       label_opts=opts.LabelOpts(is_show=False),
                       is_smooth=True
                       )
            .set_global_opts(title_opts=opts.TitleOpts(title="AV数量年份统计"))
    )
    return line.render_embed()


def get_actress_height_charts():
    result = Actress.query.with_entities(Actress.height, func.count('*').label('height_count')) \
        .filter(Actress.height.isnot(None)) \
        .order_by(Actress.height) \
        .group_by(Actress.height).all()
    a1, a2 = zip(*result)
    a1, a2 = list(a1), list(a2)
    heightlist = ['<140', '140-144', '145-149', '150-154', '155-159', '160-164', '165-169', '170-174', '175-179',
                  '>=180']
    countlist = [0] * 10
    for i in range(0, len(a1)):
        index = 0
        if 140 <= a1[i] <= 144:
            index = 1
        elif 145 <= a1[i] <= 149:
            index = 2
        elif 150 <= a1[i] <= 154:
            index = 3
        elif 155 <= a1[i] <= 159:
            index = 4
        elif 160 <= a1[i] <= 164:
            index = 5
        elif 165 <= a1[i] <= 169:
            index = 6
        elif 170 <= a1[i] <= 174:
            index = 7
        elif 175 <= a1[i] <= 179:
            index = 8
        elif a1[i] >= 180:
            index = 9
        countlist[index] = a2[i]
    bar = (
        Bar(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', ))
            .add_xaxis(heightlist)
            .add_yaxis("数量", countlist)
            .set_global_opts(title_opts=opts.TitleOpts(title="身高分布"))
        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    return bar.render_embed()


def get_cup_pie_charts():
    result = Actress.query.with_entities(Actress.cup, func.count('*').label('cup_count')) \
        .filter(Actress.cup.isnot(None)) \
        .order_by(Actress.cup) \
        .group_by(Actress.cup).all()
    pie = (
        Pie(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', )
        )
            .add("", data_pair=result)
            .set_global_opts(title_opts=opts.TitleOpts(title="CUP分布"))
    )
    return pie.render_embed()


def get_actress_num_rank():
    counts = func.count(1)
    result = Actress.query.with_entities(Actress.actname, counts) \
        .join(av_actress) \
        .order_by(counts.desc()) \
        .group_by(Actress.id) \
        .all()
    # .join(av) \
    # .filter(datetime.date(datetime.datetime.now().year-5,1,1) <= av.rdate , av.rdate < datetime.date(datetime.datetime.now().year-4,1,1)) \

    countlist = [x[1] for x in result]
    avg = round(np.mean(countlist), 2)
    median = np.median(countlist)

    actresslist = []
    countlist = []
    for i in range(15):
        actresslist.append(result[i][0])
        countlist.append(result[i][1])
    actresslist.append('平均数')
    countlist.append(avg)
    actresslist.append('中位数')
    countlist.append(median)
    bar = (
        Bar(init_opts=opts.InitOpts(
            # 设置宽度、高度
            width='1200px',
            height='500px', ))
            .add_xaxis(actresslist[::-1])
            .add_yaxis("数量", countlist[::-1])
            .set_global_opts(title_opts=opts.TitleOpts(title="数量TOP"))
        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    return bar.render_embed()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
